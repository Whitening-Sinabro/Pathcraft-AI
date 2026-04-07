# -*- coding: utf-8 -*-
"""
LLM Provider Factory
멀티 LLM 프로바이더 팩토리 (Claude, GPT, Gemini)
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


@dataclass
class LLMResponse:
    """LLM 응답 데이터"""
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and len(self.content) > 0


class BaseLLMProvider(ABC):
    """LLM 프로바이더 기본 인터페이스"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """프로바이더 이름"""
        pass

    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        """
        텍스트 생성

        Args:
            prompt: 사용자 프롬프트
            system: 시스템 프롬프트

        Returns:
            LLMResponse 객체
        """
        pass

    def estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (대략적)"""
        # 한글은 약 1.5~2 토큰/글자, 영어는 약 0.25 토큰/단어
        # 간단히 글자 수 / 2로 추정
        return len(text) // 2


class ClaudeProvider(BaseLLMProvider):
    """Claude API 프로바이더"""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self._client = None

    @property
    def provider_name(self) -> str:
        return "claude"

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic 패키지가 설치되지 않았습니다. pip install anthropic")
        return self._client

    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        import time
        start_time = time.time()

        try:
            client = self._get_client()

            message = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system if system else "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}]
            )

            elapsed = time.time() - start_time

            return LLMResponse(
                content=message.content[0].text,
                provider=self.provider_name,
                model=self.model,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                elapsed_seconds=round(elapsed, 2)
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.model,
                error=str(e),
                elapsed_seconds=round(time.time() - start_time, 2)
            )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT API 프로바이더"""

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self._client = None

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai 패키지가 설치되지 않았습니다. pip install openai")
        return self._client

    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        import time
        start_time = time.time()

        try:
            client = self._get_client()

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7
            )

            elapsed = time.time() - start_time

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                elapsed_seconds=round(elapsed, 2)
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.model,
                error=str(e),
                elapsed_seconds=round(time.time() - start_time, 2)
            )


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API 프로바이더"""

    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self._model_instance = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _get_model(self):
        if self._model_instance is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model_instance = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai 패키지가 설치되지 않았습니다. pip install google-generativeai")
        return self._model_instance

    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        import time
        start_time = time.time()

        try:
            model = self._get_model()

            # Gemini는 시스템 프롬프트를 별도로 지원하지 않으므로 프롬프트에 포함
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"

            response = model.generate_content(full_prompt)

            elapsed = time.time() - start_time

            # 토큰 정보 가져오기
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

            return LLMResponse(
                content=response.text,
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                elapsed_seconds=round(elapsed, 2)
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.model,
                error=str(e),
                elapsed_seconds=round(time.time() - start_time, 2)
            )


class GrokProvider(BaseLLMProvider):
    """xAI Grok API 프로바이더 (OpenAI SDK 호환)"""

    DEFAULT_MODEL = "grok-beta"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self._client = None

    @property
    def provider_name(self) -> str:
        return "grok"

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.x.ai/v1"
                )
            except ImportError:
                raise ImportError("openai 패키지가 설치되지 않았습니다. pip install openai")
        return self._client

    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        import time
        start_time = time.time()

        try:
            client = self._get_client()

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7
            )

            elapsed = time.time() - start_time

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model,
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                elapsed_seconds=round(elapsed, 2)
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.model,
                error=str(e),
                elapsed_seconds=round(time.time() - start_time, 2)
            )


class LLMProviderFactory:
    """LLM 프로바이더 팩토리"""

    PROVIDERS = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "grok": GrokProvider
    }

    DEFAULT_MODELS = {
        "claude": ClaudeProvider.DEFAULT_MODEL,
        "openai": OpenAIProvider.DEFAULT_MODEL,
        "gemini": GeminiProvider.DEFAULT_MODEL,
        "grok": GrokProvider.DEFAULT_MODEL
    }

    # API 키 패턴 (프로바이더 자동 감지용)
    API_KEY_PATTERNS = {
        "claude": "sk-ant-",      # Anthropic: sk-ant-api03-...
        "gemini": "AIza",         # Google: AIza...
        "grok": "xai-",           # xAI: xai-...
        "openai": "sk-"           # OpenAI: sk-... (Claude 제외)
    }

    @classmethod
    def create(cls, provider: str, api_key: str = None, model: str = None) -> BaseLLMProvider:
        """
        LLM 프로바이더 생성

        Args:
            provider: 프로바이더 이름 (claude, openai, gemini)
            api_key: API 키 (없으면 환경변수에서 가져옴)
            model: 모델 이름 (없으면 기본값 사용)

        Returns:
            BaseLLMProvider 인스턴스
        """
        provider = provider.lower()

        if provider not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(cls.PROVIDERS.keys())}")

        # API 키 가져오기
        if api_key is None:
            env_keys = {
                "claude": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"]
            }

            key_names = env_keys.get(provider)
            if isinstance(key_names, list):
                for key_name in key_names:
                    api_key = os.environ.get(key_name)
                    if api_key:
                        break
            else:
                api_key = os.environ.get(key_names)

        if not api_key:
            raise ValueError(f"API key not found for {provider}. Set environment variable or pass api_key.")

        return cls.PROVIDERS[provider](api_key, model)

    @classmethod
    def get_available_providers(cls) -> list:
        """사용 가능한 프로바이더 목록"""
        return list(cls.PROVIDERS.keys())

    @classmethod
    def check_api_key(cls, provider: str) -> bool:
        """API 키 존재 여부 확인"""
        provider = provider.lower()

        env_keys = {
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "grok": "XAI_API_KEY"
        }

        key_names = env_keys.get(provider)
        if not key_names:
            return False

        if isinstance(key_names, list):
            return any(os.environ.get(k) for k in key_names)
        return bool(os.environ.get(key_names))

    @classmethod
    def detect_provider_from_api_key(cls, api_key: str) -> Optional[str]:
        """
        API 키 패턴으로 프로바이더 자동 감지

        Args:
            api_key: 사용자가 입력한 API 키

        Returns:
            프로바이더 이름 (claude, openai, gemini, grok) 또는 None

        지원 패턴:
            - Claude: sk-ant-...
            - OpenAI: sk-... (sk-ant 제외)
            - Gemini: AIza...
            - Grok: xai-...
        """
        if not api_key:
            return None

        api_key = api_key.strip()

        # Claude: sk-ant-... (OpenAI보다 먼저 체크해야 함)
        if api_key.startswith('sk-ant-'):
            return 'claude'

        # Gemini: AIza...
        if api_key.startswith('AIza'):
            return 'gemini'

        # Grok: xai-...
        if api_key.startswith('xai-'):
            return 'grok'

        # OpenAI: sk-... (Claude가 아닌 경우)
        if api_key.startswith('sk-'):
            return 'openai'

        return None

    @classmethod
    def create_from_api_key(cls, api_key: str, model: str = None) -> BaseLLMProvider:
        """
        API 키만으로 프로바이더 자동 생성

        Args:
            api_key: API 키 (자동 감지)
            model: 모델 이름 (선택, 없으면 기본값 사용)

        Returns:
            BaseLLMProvider 인스턴스

        Raises:
            ValueError: 알 수 없는 API 키 형식

        Examples:
            >>> provider = LLMProviderFactory.create_from_api_key("sk-ant-api03-xxx")
            >>> provider.provider_name
            'claude'

            >>> provider = LLMProviderFactory.create_from_api_key("AIzaSyxxx")
            >>> provider.provider_name
            'gemini'
        """
        provider = cls.detect_provider_from_api_key(api_key)
        if not provider:
            raise ValueError(
                f"Unknown API key format. Supported patterns:\n"
                f"  - Claude: sk-ant-...\n"
                f"  - OpenAI: sk-...\n"
                f"  - Gemini: AIza...\n"
                f"  - Grok: xai-..."
            )
        return cls.create(provider, api_key, model)


if __name__ == "__main__":
    # 테스트
    print("=" * 60)
    print("LLM Provider Factory Test")
    print("=" * 60)

    print("\n사용 가능한 프로바이더:", LLMProviderFactory.get_available_providers())

    print("\nAPI 키 상태:")
    for provider in LLMProviderFactory.get_available_providers():
        status = "✓" if LLMProviderFactory.check_api_key(provider) else "✗"
        print(f"  {provider}: {status}")

    # API 키 자동 감지 테스트
    print("\n" + "=" * 60)
    print("API 키 자동 감지 테스트")
    print("=" * 60)

    test_keys = [
        ("sk-ant-api03-xxxxx", "claude"),
        ("sk-proj-xxxxx", "openai"),
        ("AIzaSyxxxxx", "gemini"),
        ("xai-xxxxx", "grok"),
        ("invalid-key", None)
    ]

    for test_key, expected in test_keys:
        detected = LLMProviderFactory.detect_provider_from_api_key(test_key)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} '{test_key[:15]}...' → {detected} (expected: {expected})")

    # API 키가 있는 프로바이더로 테스트
    print("\n" + "=" * 60)
    print("실제 API 호출 테스트")
    print("=" * 60)

    for provider in ["gemini", "claude", "openai", "grok"]:
        if LLMProviderFactory.check_api_key(provider):
            print(f"\n{provider} 테스트:")
            try:
                llm = LLMProviderFactory.create(provider)
                response = llm.generate("Hello, what is 2+2?", "You are a helpful assistant. Reply briefly.")
                if response.success:
                    print(f"  응답: {response.content[:100]}...")
                    print(f"  토큰: {response.input_tokens} in / {response.output_tokens} out")
                    print(f"  시간: {response.elapsed_seconds}s")
                else:
                    print(f"  오류: {response.error}")
            except Exception as e:
                print(f"  예외: {e}")
            break
    else:
        print("\n테스트할 API 키가 없습니다.")
