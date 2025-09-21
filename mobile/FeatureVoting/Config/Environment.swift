import Foundation

enum AppEnvironment {
    case development
    case staging
    case production

    static var current: AppEnvironment {
        #if DEBUG
        return .development
        #elseif STAGING
        return .staging
        #else
        return .production
        #endif
    }

    var apiBaseURL: String {
        switch self {
        case .development:
            return "http://localhost:8000"
        case .staging:
            return "https://staging-api.featurevoting.com"
        case .production:
            return "https://api.featurevoting.com"
        }
    }

    var apiVersion: String {
        return "api"
    }

    var fullAPIURL: String {
        return "\(apiBaseURL)/\(apiVersion)"
    }

    var networkTimeout: TimeInterval {
        switch self {
        case .development:
            return 30.0
        case .staging, .production:
            return 15.0
        }
    }

    var isDebugMode: Bool {
        switch self {
        case .development:
            return true
        case .staging, .production:
            return false
        }
    }
}

struct AppConfig {
    static let environment = AppEnvironment.current
    static let apiBaseURL = environment.fullAPIURL
    static let networkTimeout = environment.networkTimeout
    static let isDebugMode = environment.isDebugMode

    // Default user ID for development/demo purposes
    static let defaultUserId = 1
}