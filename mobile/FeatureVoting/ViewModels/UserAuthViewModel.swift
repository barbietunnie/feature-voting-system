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
        let trimmedUsername = username.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines)

        return trimmedUsername.count >= 2 &&
               trimmedUsername.count <= 50 &&
               !trimmedEmail.isEmpty &&
               isValidEmail(trimmedEmail)
    }

    var usernameValidationMessage: String? {
        let trimmed = username.trimmingCharacters(in: .whitespacesAndNewlines)
        if !username.isEmpty && trimmed.count < 2 {
            return "Username must be at least 2 characters"
        }
        if trimmed.count > 50 {
            return "Username must not exceed 50 characters"
        }
        return nil
    }

    var emailValidationMessage: String? {
        if !email.isEmpty && !isValidEmail(email) {
            return "Please enter a valid email address"
        }
        return nil
    }

    func loadExistingUsers() async {
        isLoading = true
        errorMessage = nil

        do {
            let users = try await apiService.fetchUsers()
            existingUsers = users
        } catch {
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
            } else {
                errorMessage = "Failed to load users: \(error.localizedDescription)"
            }
            if AppConfig.isDebugMode {
                print("Error loading users: \(error)")
            }
        }

        isLoading = false
    }

    func createNewUser() async -> Bool {
        if let usernameError = usernameValidationMessage {
            errorMessage = usernameError
            return false
        }

        if let emailError = emailValidationMessage {
            errorMessage = emailError
            return false
        }

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
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
            } else {
                errorMessage = "Failed to create user: \(error.localizedDescription)"
            }
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