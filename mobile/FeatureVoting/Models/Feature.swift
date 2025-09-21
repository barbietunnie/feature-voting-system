import Foundation

enum FeatureStatus: String, Codable, CaseIterable {
    case pending = "pending"
    case inProgress = "in_progress"
    case completed = "completed"
    case rejected = "rejected"

    var displayName: String {
        switch self {
        case .pending: return "Pending"
        case .inProgress: return "In Progress"
        case .completed: return "Completed"
        case .rejected: return "Rejected"
        }
    }
}

struct Feature: Codable, Identifiable {
    let id: Int
    let title: String
    let description: String
    let status: FeatureStatus
    let createdBy: Int
    let createdAt: Date
    let updatedAt: Date?
    let voteCount: Int?

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case status
        case createdBy = "created_by"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case voteCount = "vote_count"
    }
}

struct FeatureCreate: Codable {
    let title: String
    let description: String
}