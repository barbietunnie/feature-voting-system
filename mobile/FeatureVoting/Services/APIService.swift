import Foundation

class APIService: ObservableObject {
    private let baseURL = AppConfig.apiBaseURL
    private let session: URLSession
    private let jsonDecoder: JSONDecoder
    private let jsonEncoder: JSONEncoder
    private let sessionManager = UserSessionManager()

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = AppConfig.networkTimeout
        config.timeoutIntervalForResource = AppConfig.networkTimeout * 2
        self.session = URLSession(configuration: config)

        self.jsonDecoder = JSONDecoder()
        self.jsonDecoder.dateDecodingStrategy = .iso8601

        self.jsonEncoder = JSONEncoder()
        self.jsonEncoder.dateEncodingStrategy = .iso8601
    }

    // MARK: - Features

    func fetchFeatures(pagination: PaginationParams = PaginationParams()) async throws -> PaginatedResponse<Feature> {
        var urlComponents = URLComponents(string: "\(baseURL)/features")!
        urlComponents.queryItems = pagination.queryItems

        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }

        let request = URLRequest(url: url)

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(PaginatedResponse<Feature>.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    func createFeature(_ feature: FeatureCreate) async throws -> Feature {
        guard let url = URL(string: "\(baseURL)/features") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("\(sessionManager.currentUserId)", forHTTPHeaderField: "X-User-ID")
        request.httpBody = try jsonEncoder.encode(feature)

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(Feature.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    func getFeature(id: Int) async throws -> Feature {
        guard let url = URL(string: "\(baseURL)/features/\(id)") else {
            throw APIError.invalidURL
        }

        let request = URLRequest(url: url)

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(Feature.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    // MARK: - Voting

    func voteForFeature(featureId: Int) async throws -> VoteResponse {
        guard let url = URL(string: "\(baseURL)/features/\(featureId)/vote") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("\(sessionManager.currentUserId)", forHTTPHeaderField: "X-User-ID")

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(VoteResponse.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    func removeVote(featureId: Int) async throws -> VoteResponse {
        guard let url = URL(string: "\(baseURL)/features/\(featureId)/vote") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("\(sessionManager.currentUserId)", forHTTPHeaderField: "X-User-ID")

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(VoteResponse.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    // MARK: - Users

    func fetchUsers() async throws -> [User] {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        let request = URLRequest(url: url)

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode([User].self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    func createUser(_ user: UserCreate) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try jsonEncoder.encode(user)

        do {
            let (data, response) = try await session.data(for: request)
            try validateResponse(response, data: data)
            return try jsonDecoder.decode(User.self, from: data)
        } catch {
            throw await handleNetworkError(error)
        }
    }

    // MARK: - Helper Methods

    private func validateResponse(_ response: URLResponse, data: Data? = nil) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return
        case 400:
            if let data = data, let errorResponse = try? JSONDecoder().decode(ServerErrorResponse.self, from: data) {
                throw APIError.serverErrorWithMessage(errorResponse.detail)
            }
            throw APIError.badRequest
        case 401:
            throw APIError.unauthorized
        case 404:
            if let data = data, let errorResponse = try? JSONDecoder().decode(ServerErrorResponse.self, from: data) {
                throw APIError.serverErrorWithMessage(errorResponse.detail)
            }
            throw APIError.notFound
        case 409:
            if let data = data, let errorResponse = try? JSONDecoder().decode(ServerErrorResponse.self, from: data) {
                throw APIError.conflictWithMessage(errorResponse.detail)
            }
            throw APIError.conflict
        case 422:
            if let data = data, let errorResponse = try? JSONDecoder().decode(ValidationErrorResponse.self, from: data) {
                let errorMessages = errorResponse.errors?.joined(separator: ", ") ?? errorResponse.detail
                throw APIError.validationErrorWithMessage(errorMessages)
            }
            throw APIError.validationError
        case 500...599:
            if let data = data, let errorResponse = try? JSONDecoder().decode(ServerErrorResponse.self, from: data) {
                throw APIError.serverErrorWithMessage(errorResponse.detail)
            }
            throw APIError.serverError
        default:
            throw APIError.invalidResponse
        }
    }

    private func handleNetworkError(_ error: Error) async -> APIError {
        if let apiError = error as? APIError {
            return apiError
        }

        if let urlError = error as? URLError {
            switch urlError.code {
            case .notConnectedToInternet, .networkConnectionLost:
                return .noInternetConnection
            case .timedOut:
                return .timeout
            case .cancelled:
                return .networkError
            case .cannotFindHost, .cannotConnectToHost, .dnsLookupFailed:
                return .networkError
            default:
                return .networkError
            }
        }

        if error is DecodingError {
            return .decodingError
        }

        if error is EncodingError {
            return .encodingError
        }

        return .networkError
    }
}

struct VoteResponse: Codable {
    let message: String
    let voteCount: Int

    enum CodingKeys: String, CodingKey {
        case message
        case voteCount = "vote_count"
    }
}

struct ServerErrorResponse: Codable {
    let detail: String
    let errorCode: String?
    let timestamp: String?
    let path: String?

    enum CodingKeys: String, CodingKey {
        case detail
        case errorCode = "error_code"
        case timestamp
        case path
    }
}

struct ValidationErrorResponse: Codable {
    let detail: String
    let errors: [String]?
    let type: String?
}

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError
    case encodingError
    case badRequest
    case unauthorized
    case notFound
    case validationError
    case serverError
    case networkError
    case conflict
    case timeout
    case noInternetConnection

    case serverErrorWithMessage(String)
    case validationErrorWithMessage(String)
    case conflictWithMessage(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .decodingError:
            return "Failed to decode response"
        case .encodingError:
            return "Failed to encode request"
        case .badRequest:
            return "Bad request"
        case .unauthorized:
            return "Please check your login credentials"
        case .notFound:
            return "Resource not found"
        case .validationError:
            return "Please check your input"
        case .serverError:
            return "Server error occurred. Please try again later"
        case .networkError:
            return "Network error. Please check your connection"
        case .conflict:
            return "This action conflicts with existing data"
        case .timeout:
            return "Request timed out. Please try again"
        case .noInternetConnection:
            return "No internet connection available"
        case .serverErrorWithMessage(let message):
            return message
        case .validationErrorWithMessage(let message):
            return message
        case .conflictWithMessage(let message):
            return message
        }
    }

    var userFriendlyMessage: String {
        switch self {
        case .invalidURL, .invalidResponse, .decodingError, .encodingError:
            return "Something went wrong. Please try again"
        case .badRequest:
            return "Invalid request. Please check your input"
        case .unauthorized:
            return "Please log in again"
        case .notFound:
            return "The requested item was not found"
        case .validationError:
            return "Please check your input and try again"
        case .serverError:
            return "Server is having issues. Please try again later"
        case .networkError, .timeout:
            return "Please check your internet connection and try again"
        case .noInternetConnection:
            return "No internet connection. Please connect and try again"
        case .conflict:
            return "This action is not allowed at this time"
        case .serverErrorWithMessage(let message),
             .validationErrorWithMessage(let message),
             .conflictWithMessage(let message):
            return message
        }
    }
}