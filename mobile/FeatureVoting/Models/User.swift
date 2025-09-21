import Foundation

struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case username
        case email
        case createdAt = "created_at"
    }
}

struct UserCreate: Codable {
    let username: String
    let email: String
}