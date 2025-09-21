import Foundation

struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String
    let isActive: Bool
    let createdAt: Date
    let updatedAt: Date?

    enum CodingKeys: String, CodingKey {
        case id
        case username
        case email
        case isActive = "is_active"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

struct UserCreate: Codable {
    let username: String
    let email: String
    let password: String
}