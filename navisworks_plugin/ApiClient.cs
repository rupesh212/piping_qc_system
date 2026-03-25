using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace PipingQCPlugin
{
    public class ApiClient
    {
        private readonly HttpClient _client;
        private readonly string _baseUrl;
        private string _token;

        public ApiClient(string baseUrl)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _client = new HttpClient();
            _client.Timeout = TimeSpan.FromSeconds(30);
        }

        /// <summary>
        /// Authenticates against POST /api/v1/auth/login using JSON body.
        /// Stores the returned JWT token for subsequent requests.
        /// Returns true on success, false on invalid credentials.
        /// Throws HttpRequestException for network or unexpected server errors.
        /// </summary>
        public async Task<bool> LoginAsync(string username, string password)
        {
            var payload = new { username = username, password = password };
            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            HttpResponseMessage response;
            try
            {
                response = await _client.PostAsync($"{_baseUrl}/api/v1/auth/login", content).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new HttpRequestException($"Network error connecting to {_baseUrl}: {ex.Message}", ex);
            }

            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                return false;

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                throw new HttpRequestException($"Login failed with status {(int)response.StatusCode}: {errorBody}");
            }

            var responseBody = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var tokenResponse = JsonConvert.DeserializeObject<TokenResponse>(responseBody);
            if (tokenResponse == null || string.IsNullOrEmpty(tokenResponse.AccessToken))
                return false;

            _token = tokenResponse.AccessToken;
            SetAuthHeader();
            return true;
        }

        /// <summary>
        /// Fetches a paginated list of ISO drawings from GET /api/v1/iso.
        /// </summary>
        public async Task<ISOListResponse> GetISOListAsync(int skip = 0, int limit = 20)
        {
            EnsureAuthenticated();
            var url = $"{_baseUrl}/api/v1/iso/?skip={skip}&limit={limit}";

            HttpResponseMessage response;
            try
            {
                response = await _client.GetAsync(url).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new HttpRequestException($"Network error fetching ISO list: {ex.Message}", ex);
            }

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                throw new HttpRequestException($"GetISOList failed with status {(int)response.StatusCode}: {errorBody}");
            }

            var body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var result = JsonConvert.DeserializeObject<ISOListResponse>(body);
            return result ?? new ISOListResponse { Items = Array.Empty<ISOItem>(), Total = 0 };
        }

        /// <summary>
        /// Triggers validation for the given ISO id via POST /api/v1/iso/{isoId}/validate.
        /// </summary>
        public async Task<ValidationResponse> ValidateISOAsync(string isoId)
        {
            EnsureAuthenticated();
            var url = $"{_baseUrl}/api/v1/iso/{isoId}/validate";

            HttpResponseMessage response;
            try
            {
                response = await _client.PostAsync(url, null).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new HttpRequestException($"Network error validating ISO {isoId}: {ex.Message}", ex);
            }

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                throw new HttpRequestException($"ValidateISO failed with status {(int)response.StatusCode}: {errorBody}");
            }

            var body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var result = JsonConvert.DeserializeObject<ValidationResponse>(body);
            return result ?? new ValidationResponse { Results = Array.Empty<ValidationResult>() };
        }

        /// <summary>
        /// Fetches aggregated dashboard KPIs from GET /api/v1/dashboard/summary.
        /// </summary>
        public async Task<DashboardSummary> GetDashboardSummaryAsync()
        {
            EnsureAuthenticated();
            var url = $"{_baseUrl}/api/v1/dashboard/summary";

            HttpResponseMessage response;
            try
            {
                response = await _client.GetAsync(url).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                throw new HttpRequestException($"Network error fetching dashboard summary: {ex.Message}", ex);
            }

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                throw new HttpRequestException($"GetDashboardSummary failed with status {(int)response.StatusCode}: {errorBody}");
            }

            var body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var result = JsonConvert.DeserializeObject<DashboardSummary>(body);
            return result ?? new DashboardSummary();
        }

        private void SetAuthHeader()
        {
            if (!string.IsNullOrEmpty(_token))
                _client.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", _token);
        }

        private void EnsureAuthenticated()
        {
            if (string.IsNullOrEmpty(_token))
                throw new InvalidOperationException("Not authenticated. Call LoginAsync first.");
        }
    }

    // Internal token deserialization DTO
    internal class TokenResponse
    {
        [JsonProperty("access_token")] public string AccessToken { get; set; }
        [JsonProperty("token_type")] public string TokenType { get; set; }
    }

    // Response DTOs
    public class ISOListResponse
    {
        [JsonProperty("items")] public ISOItem[] Items { get; set; }
        [JsonProperty("total")] public int Total { get; set; }
    }

    public class ISOItem
    {
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("file_name")] public string FileName { get; set; }
        [JsonProperty("line_number")] public string LineNumber { get; set; }
        [JsonProperty("pipe_size")] public string PipeSize { get; set; }
        [JsonProperty("spec")] public string Spec { get; set; }
        [JsonProperty("status")] public string Status { get; set; }
    }

    public class ValidationResponse
    {
        [JsonProperty("results")] public ValidationResult[] Results { get; set; }
    }

    public class ValidationResult
    {
        [JsonProperty("rule_name")] public string RuleName { get; set; }
        [JsonProperty("result")] public string Result { get; set; }
        [JsonProperty("message")] public string Message { get; set; }
    }

    public class DashboardSummary
    {
        [JsonProperty("total_isos")] public int TotalIsos { get; set; }
        [JsonProperty("total_lines")] public int TotalLines { get; set; }
        [JsonProperty("total_validations")] public int TotalValidations { get; set; }
        [JsonProperty("total_errors")] public int TotalErrors { get; set; }
        [JsonProperty("pass_rate")] public double PassRate { get; set; }
    }
}
