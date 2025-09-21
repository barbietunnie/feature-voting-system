import Foundation

@MainActor
class UserAuthViewModel: ObservableObject {
    @Published var username = ""
    @Published var email = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var existingUsers: [User] = []

    private let apiService = APIService()
    var sessionManager: UserSessionManager?

    var isFormValid: Bool {
        !username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        isValidEmail(email)
    }

    func loadExistingUsers() async {
        isLoading = true
        errorMessage = nil

        do {
            let users = try await apiService.fetchUsers()
            existingUsers = users
        } catch {
            errorMessage = "Failed to load users: \(error.localizedDescription)"
            if AppConfig.isDebugMode {
                print("Error loading users: \(error)")
            }
        }

        isLoading = false
    }

    func createNewUser() async -> Bool {
        guard isFormValid else {
            errorMessage = "Please fill in all fields with valid information"
            return false
        }

        isLoading = true
        errorMessage = nil

        let newUser = UserCreate(
            username: username.trimmingCharacters(in: .whitespacesAndNewlines),
            email: email.trimmingCharacters(in: .whitespacesAndNewlines)
        )

        do {
            let createdUser = try await apiService.createUser(newUser)
            sessionManager?.login(user: createdUser)
            return true
        } catch {
            errorMessage = "Failed to create user: \(error.localizedDescription)"
            if AppConfig.isDebugMode {
                print("Error creating user: \(error)")
            }
            return false
        }
    }

    func selectExistingUser(_ user: User) {
        sessionManager?.login(user: user)
    }

    func clearError() {
        errorMessage = nil
    }

    private func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }
}