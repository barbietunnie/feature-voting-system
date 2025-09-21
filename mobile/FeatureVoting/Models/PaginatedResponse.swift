import Foundation

struct PaginatedResponse<T: Codable>: Codable {
    let items: [T]
    let totalCount: Int
    let page: Int
    let pageSize: Int
    let totalPages: Int
    let hasNext: Bool
    let hasPrevious: Bool

    enum CodingKeys: String, CodingKey {
        case items
        case totalCount = "total_count"
        case page
        case pageSize = "page_size"
        case totalPages = "total_pages"
        case hasNext = "has_next"
        case hasPrevious = "has_previous"
    }
}

struct PaginationParams {
    let page: Int
    let pageSize: Int

    init(page: Int = 1, pageSize: Int = 20) {
        self.page = max(1, page)
        self.pageSize = min(max(1, pageSize), 100)
    }

    var queryItems: [URLQueryItem] {
        return [
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "page_size", value: String(pageSize))
        ]
    }
}