import Foundation

class APIService: ObservableObject {
    private let baseURL = AppConfig.apiBaseURL
    private let session: URLSession
    private let jsonDecoder: JSONDecoder
    private let jsonEncoder: JSONEncoder

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
        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(PaginatedResponse<Feature>.self, from: data)
    }

    func createFeature(_ feature: FeatureCreate) async throws -> Feature {
        guard let url = URL(string: "\(baseURL)/features") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("\(AppConfig.defaultUserId)", forHTTPHeaderField: "X-User-ID")
        request.httpBody = try jsonEncoder.encode(feature)

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(Feature.self, from: data)
    }

    func getFeature(id: Int) async throws -> Feature {
        guard let url = URL(string: "\(baseURL)/features/\(id)") else {
            throw APIError.invalidURL
        }

        let request = URLRequest(url: url)
        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(Feature.self, from: data)
    }

    // MARK: - Voting

    func voteForFeature(featureId: Int) async throws -> VoteResponse {
        guard let url = URL(string: "\(baseURL)/features/\(featureId)/vote") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("\(AppConfig.defaultUserId)", forHTTPHeaderField: "X-User-ID")

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(VoteResponse.self, from: data)
    }

    func removeVote(featureId: Int) async throws -> VoteResponse {
        guard let url = URL(string: "\(baseURL)/features/\(featureId)/vote") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("\(AppConfig.defaultUserId)", forHTTPHeaderField: "X-User-ID")

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(VoteResponse.self, from: data)
    }

    // MARK: - Users

    func createUser(_ user: UserCreate) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try jsonEncoder.encode(user)

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        return try jsonDecoder.decode(User.self, from: data)
    }

    // MARK: - Helper Methods

    private func validateResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return
        case 400:
            throw APIError.badRequest
        case 401:
            throw APIError.unauthorized
        case 404:
            throw APIError.notFound
        case 422:
            throw APIError.validationError
        case 500...599:
            throw APIError.serverError
        default:
            throw APIError.invalidResponse
        }
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
            return "Unauthorized access"
        case .notFound:
            return "Resource not found"
        case .validationError:
            return "Validation error"
        case .serverError:
            return "Server error"
        case .networkError:
            return "Network error"
        }
    }
}