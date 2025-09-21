import Foundation

struct Feature: Codable, Identifiable {
    let id: Int
    let title: String
    let description: String
    let authorId: Int
    let createdAt: Date
    let voteCount: Int

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case authorId = "author_id"
        case createdAt = "created_at"
        case voteCount = "vote_count"
    }
}

struct FeatureCreate: Codable {
    let title: String
    let description: String
}