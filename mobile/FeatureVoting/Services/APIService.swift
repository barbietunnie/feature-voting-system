import Foundation

class APIService: ObservableObject {
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared

    func fetchFeatures() async throws -> [Feature] {
        guard let url = URL(string: "\(baseURL)/features/") else {
            throw APIError.invalidURL
        }

        let (data, _) = try await session.data(from: url)
        let features = try JSONDecoder().decode([Feature].self, from: data)
        return features
    }

    func createFeature(_ feature: FeatureCreate) async throws -> Feature {
        guard let url = URL(string: "\(baseURL)/features/") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(feature)

        let (data, _) = try await session.data(for: request)
        let createdFeature = try JSONDecoder().decode(Feature.self, from: data)
        return createdFeature
    }

    func createVote(_ vote: VoteCreate) async throws -> Vote {
        guard let url = URL(string: "\(baseURL)/votes/") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(vote)

        let (data, _) = try await session.data(for: request)
        let createdVote = try JSONDecoder().decode(Vote.self, from: data)
        return createdVote
    }
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case decodingError
}