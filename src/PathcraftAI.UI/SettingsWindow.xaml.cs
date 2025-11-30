using System;
using System.IO;
using System.Windows;
using Microsoft.Win32;
using Newtonsoft.Json;

namespace PathcraftAI.UI
{
    public partial class SettingsWindow : Window
    {
        private readonly AppSettings _settings;

        public SettingsWindow()
        {
            InitializeComponent();
            _settings = AppSettings.Load();
            LoadSettingsToUI();
        }

        private void LoadSettingsToUI()
        {
            // Universal API Key
            UniversalApiKeyBox.Text = _settings.UniversalApiKey ?? "";
            UpdateDetectedProvider(_settings.UniversalApiKey ?? "");

            // API Keys
            ClaudeApiKeyBox.Text = _settings.ClaudeApiKey ?? "";
            GptApiKeyBox.Text = _settings.GptApiKey ?? "";
            GeminiApiKeyBox.Text = _settings.GeminiApiKey ?? "";
            GrokApiKeyBox.Text = _settings.GrokApiKey ?? "";
            YouTubeApiKeyBox.Text = _settings.YouTubeApiKey ?? "";

            // Game Settings
            SelectComboBoxItem(LeagueComboBox, _settings.DefaultLeague ?? "Keepers");
            BudgetBox.Text = _settings.DefaultBudget.ToString();

            // Python Settings
            PythonPathBox.Text = _settings.PythonPath ?? @".venv\Scripts\python.exe";

            // UI Settings
            SelectComboBoxItem(AiProviderComboBox, _settings.DefaultAiProvider ?? "Rule-Based (Free)");
        }

        private void UniversalApiKey_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            var apiKey = UniversalApiKeyBox.Text.Trim();
            UpdateDetectedProvider(apiKey);
        }

        private void UpdateDetectedProvider(string apiKey)
        {
            if (string.IsNullOrEmpty(apiKey))
            {
                DetectedProviderText.Text = "";
                return;
            }

            var provider = DetectProviderFromApiKey(apiKey);
            if (provider != null)
            {
                DetectedProviderText.Text = $"[{provider.ToUpper()}]";
                DetectedProviderText.Foreground = new System.Windows.Media.SolidColorBrush(
                    System.Windows.Media.Color.FromRgb(166, 227, 161)); // Green
            }
            else
            {
                DetectedProviderText.Text = "[?]";
                DetectedProviderText.Foreground = new System.Windows.Media.SolidColorBrush(
                    System.Windows.Media.Color.FromRgb(243, 139, 168)); // Red
            }
        }

        /// <summary>
        /// Detect LLM provider from API key pattern
        /// </summary>
        private static string? DetectProviderFromApiKey(string apiKey)
        {
            if (string.IsNullOrEmpty(apiKey)) return null;

            // Claude: sk-ant-api03-xxxxx
            if (apiKey.StartsWith("sk-ant-")) return "claude";

            // Gemini: AIzaSyxxxxx
            if (apiKey.StartsWith("AIza")) return "gemini";

            // Grok: xai-xxxxx
            if (apiKey.StartsWith("xai-")) return "grok";

            // OpenAI: sk-xxxxx (but not sk-ant)
            if (apiKey.StartsWith("sk-")) return "openai";

            return null;
        }

        private void SelectComboBoxItem(System.Windows.Controls.ComboBox comboBox, string value)
        {
            foreach (System.Windows.Controls.ComboBoxItem item in comboBox.Items)
            {
                if (item.Content?.ToString() == value)
                {
                    comboBox.SelectedItem = item;
                    return;
                }
            }
        }

        private void BrowsePython_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Title = "Select Python Executable",
                Filter = "Python Executable|python.exe;python3.exe|All Files|*.*",
                InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles)
            };

            if (dialog.ShowDialog() == true)
            {
                PythonPathBox.Text = dialog.FileName;
            }
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validate budget
                if (!int.TryParse(BudgetBox.Text, out int budget) || budget < 0)
                {
                    MessageBox.Show("Invalid budget value. Please enter a positive number.",
                        "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // Save settings
                _settings.UniversalApiKey = UniversalApiKeyBox.Text.Trim();
                _settings.ClaudeApiKey = ClaudeApiKeyBox.Text.Trim();
                _settings.GptApiKey = GptApiKeyBox.Text.Trim();
                _settings.GeminiApiKey = GeminiApiKeyBox.Text.Trim();
                _settings.GrokApiKey = GrokApiKeyBox.Text.Trim();
                _settings.YouTubeApiKey = YouTubeApiKeyBox.Text.Trim();

                // Auto-distribute universal key to specific provider
                var universalKey = _settings.UniversalApiKey;
                if (!string.IsNullOrEmpty(universalKey))
                {
                    var detectedProvider = DetectProviderFromApiKey(universalKey);
                    switch (detectedProvider)
                    {
                        case "claude":
                            _settings.ClaudeApiKey = universalKey;
                            break;
                        case "openai":
                            _settings.GptApiKey = universalKey;
                            break;
                        case "gemini":
                            _settings.GeminiApiKey = universalKey;
                            break;
                        case "grok":
                            _settings.GrokApiKey = universalKey;
                            break;
                    }
                }

                _settings.DefaultLeague = (LeagueComboBox.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content?.ToString() ?? "Keepers";
                _settings.DefaultBudget = budget;

                _settings.PythonPath = PythonPathBox.Text.Trim();
                _settings.DefaultAiProvider = (AiProviderComboBox.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content?.ToString() ?? "Rule-Based (Free)";

                _settings.Save();

                DialogResult = true;
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to save settings:\n{ex.Message}",
                    "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }

    /// <summary>
    /// Application settings that are persisted to config.json
    /// </summary>
    public class AppSettings
    {
        private static readonly string ConfigPath = Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory, "config.json");

        // API Keys
        public string? UniversalApiKey { get; set; }  // Auto-detect provider
        public string? ClaudeApiKey { get; set; }
        public string? GptApiKey { get; set; }
        public string? GeminiApiKey { get; set; }
        public string? GrokApiKey { get; set; }
        public string? YouTubeApiKey { get; set; }

        // Game Settings
        public string? DefaultLeague { get; set; } = "Keepers";
        public int DefaultBudget { get; set; } = 100;

        // Python Settings
        public string? PythonPath { get; set; } = @".venv\Scripts\python.exe";

        // UI Settings
        public string? DefaultAiProvider { get; set; } = "Rule-Based (Free)";

        // Backup Settings
        public bool AutoBackupOnExit { get; set; } = true;

        /// <summary>
        /// Load settings from config.json, or create default if not exists
        /// </summary>
        public static AppSettings Load()
        {
            try
            {
                if (File.Exists(ConfigPath))
                {
                    var json = File.ReadAllText(ConfigPath);
                    return JsonConvert.DeserializeObject<AppSettings>(json) ?? new AppSettings();
                }
            }
            catch (Exception)
            {
                // If loading fails, return default settings
            }

            return new AppSettings();
        }

        /// <summary>
        /// Save settings to config.json
        /// </summary>
        public void Save()
        {
            var json = JsonConvert.SerializeObject(this, Formatting.Indented);
            File.WriteAllText(ConfigPath, json);
        }

        /// <summary>
        /// Get API key from settings or environment variable
        /// </summary>
        public string? GetApiKey(string provider)
        {
            return provider.ToLower() switch
            {
                "claude" => !string.IsNullOrEmpty(ClaudeApiKey)
                    ? ClaudeApiKey
                    : Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY"),
                "gpt" or "openai" => !string.IsNullOrEmpty(GptApiKey)
                    ? GptApiKey
                    : Environment.GetEnvironmentVariable("OPENAI_API_KEY"),
                "gemini" or "google" => !string.IsNullOrEmpty(GeminiApiKey)
                    ? GeminiApiKey
                    : Environment.GetEnvironmentVariable("GOOGLE_API_KEY"),
                "grok" or "xai" => !string.IsNullOrEmpty(GrokApiKey)
                    ? GrokApiKey
                    : Environment.GetEnvironmentVariable("XAI_API_KEY"),
                "youtube" => !string.IsNullOrEmpty(YouTubeApiKey)
                    ? YouTubeApiKey
                    : Environment.GetEnvironmentVariable("YOUTUBE_API_KEY"),
                _ => null
            };
        }

        /// <summary>
        /// Get the best available API key and its detected provider
        /// Returns (apiKey, provider) tuple
        /// </summary>
        public (string? ApiKey, string? Provider) GetBestAvailableApiKey()
        {
            // 1. Universal key (auto-detect)
            if (!string.IsNullOrEmpty(UniversalApiKey))
            {
                var provider = DetectProviderFromApiKey(UniversalApiKey);
                if (provider != null)
                    return (UniversalApiKey, provider);
            }

            // 2. Specific keys in priority order
            if (!string.IsNullOrEmpty(ClaudeApiKey))
                return (ClaudeApiKey, "claude");
            if (!string.IsNullOrEmpty(GptApiKey))
                return (GptApiKey, "openai");
            if (!string.IsNullOrEmpty(GeminiApiKey))
                return (GeminiApiKey, "gemini");
            if (!string.IsNullOrEmpty(GrokApiKey))
                return (GrokApiKey, "grok");

            // 3. Environment variables
            var envClaude = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY");
            if (!string.IsNullOrEmpty(envClaude))
                return (envClaude, "claude");

            var envOpenAI = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
            if (!string.IsNullOrEmpty(envOpenAI))
                return (envOpenAI, "openai");

            var envGemini = Environment.GetEnvironmentVariable("GOOGLE_API_KEY");
            if (!string.IsNullOrEmpty(envGemini))
                return (envGemini, "gemini");

            var envGrok = Environment.GetEnvironmentVariable("XAI_API_KEY");
            if (!string.IsNullOrEmpty(envGrok))
                return (envGrok, "grok");

            return (null, null);
        }

        /// <summary>
        /// Detect LLM provider from API key pattern
        /// </summary>
        public static string? DetectProviderFromApiKey(string? apiKey)
        {
            if (string.IsNullOrEmpty(apiKey)) return null;

            // Claude: sk-ant-api03-xxxxx
            if (apiKey.StartsWith("sk-ant-")) return "claude";

            // Gemini: AIzaSyxxxxx
            if (apiKey.StartsWith("AIza")) return "gemini";

            // Grok: xai-xxxxx
            if (apiKey.StartsWith("xai-")) return "grok";

            // OpenAI: sk-xxxxx (but not sk-ant)
            if (apiKey.StartsWith("sk-")) return "openai";

            return null;
        }

        /// <summary>
        /// Get the resolved Python path (from settings or auto-detected)
        /// </summary>
        public string GetResolvedPythonPath(string parserDir)
        {
            // 1. 사용자가 명시적으로 설정한 경로 확인
            if (!string.IsNullOrEmpty(PythonPath) && PythonPath != @".venv\Scripts\python.exe")
            {
                if (File.Exists(PythonPath))
                    return PythonPath;
            }

            // 2. 자동 감지 시도
            var detectedPath = AutoDetectPythonPath(parserDir);
            if (!string.IsNullOrEmpty(detectedPath))
                return detectedPath;

            // 3. 기본값 반환 (상대 경로)
            return Path.Combine(parserDir, ".venv", "Scripts", "python.exe");
        }

        /// <summary>
        /// Auto-detect Python venv path
        /// </summary>
        public static string? AutoDetectPythonPath(string parserDir)
        {
            // Windows 경로들
            var windowsPaths = new[]
            {
                Path.Combine(parserDir, ".venv", "Scripts", "python.exe"),
                Path.Combine(parserDir, "venv", "Scripts", "python.exe"),
                Path.Combine(parserDir, ".venv", "Scripts", "python3.exe"),
            };

            // Unix/macOS 경로들
            var unixPaths = new[]
            {
                Path.Combine(parserDir, ".venv", "bin", "python"),
                Path.Combine(parserDir, "venv", "bin", "python"),
                Path.Combine(parserDir, ".venv", "bin", "python3"),
            };

            // 플랫폼에 따라 경로 선택
            var pathsToCheck = Environment.OSVersion.Platform == PlatformID.Win32NT
                ? windowsPaths
                : unixPaths;

            foreach (var path in pathsToCheck)
            {
                if (File.Exists(path))
                    return path;
            }

            // 시스템 Python 확인 (최후의 수단)
            var systemPython = Environment.OSVersion.Platform == PlatformID.Win32NT
                ? "python.exe"
                : "python3";

            // PATH에서 python 찾기
            var pathEnv = Environment.GetEnvironmentVariable("PATH") ?? "";
            var pathDirs = pathEnv.Split(Path.PathSeparator);

            foreach (var dir in pathDirs)
            {
                var pythonPath = Path.Combine(dir, systemPython);
                if (File.Exists(pythonPath))
                    return pythonPath;
            }

            return null;
        }
    }
}
