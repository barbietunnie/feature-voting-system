import Foundation

class UserSessionManager: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoggedIn: Bool = false

    private let userDefaults = UserDefaults.standard
    private let currentUserKey = "currentUser"

    init() {
        loadCurrentUser()
    }

    func login(user: User) {
        currentUser = user
        isLoggedIn = true
        saveCurrentUser(user)
    }

    func logout() {
        currentUser = nil
        isLoggedIn = false
        userDefaults.removeObject(forKey: currentUserKey)
    }

    private func saveCurrentUser(_ user: User) {
        if let encoded = try? JSONEncoder().encode(user) {
            userDefaults.set(encoded, forKey: currentUserKey)
        }
    }

    private func loadCurrentUser() {
        if let data = userDefaults.data(forKey: currentUserKey),
           let user = try? JSONDecoder().decode(User.self, from: data) {
            currentUser = user
            isLoggedIn = true
        }
    }

    var currentUserId: Int {
        return currentUser?.id ?? AppConfig.defaultUserId
    }
}