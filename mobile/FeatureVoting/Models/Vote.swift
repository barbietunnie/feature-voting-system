import Foundation

struct Vote: Codable, Identifiable {
    let id: Int
    let userId: Int
    let featureId: Int
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case featureId = "feature_id"
        case createdAt = "created_at"
    }
}

struct VoteCreate: Codable {
    let featureId: Int

    enum CodingKeys: String, CodingKey {
        case featureId = "feature_id"
    }
}