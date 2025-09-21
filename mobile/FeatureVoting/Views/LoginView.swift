import SwiftUI

struct LoginView: View {
    @StateObject private var viewModel = UserAuthViewModel()
    @EnvironmentObject var sessionManager: UserSessionManager
    @State private var showingCreateUser = false

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 16) {
                    Image(systemName: "person.3.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)

                    VStack(spacing: 4) {
                        Text("Feature Voting")
                            .font(.largeTitle)
                            .fontWeight(.bold)

                        Text("Select or create your user profile")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                }
                .padding(.top, 40)

                Spacer()

                // Existing Users Section
                if viewModel.isLoading && viewModel.existingUsers.isEmpty {
                    ProgressView("Loading users...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if !viewModel.existingUsers.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Select Existing User")
                            .font(.headline)

                        LazyVStack(spacing: 8) {
                            ForEach(viewModel.existingUsers) { user in
                                UserRowView(user: user) {
                                    sessionManager.login(user: user)
                                }
                            }
                        }
                        .frame(maxHeight: 200)
                    }
                }

                // Create New User Button
                VStack(spacing: 16) {
                    Button("Create New User") {
                        showingCreateUser = true
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                    if let errorMessage = viewModel.errorMessage {
                        ErrorBanner(message: errorMessage) {
                            viewModel.clearError()
                        }
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Welcome")
            .navigationBarTitleDisplayMode(.inline)
            .task {
                viewModel.sessionManager = sessionManager
                await viewModel.loadExistingUsers()
            }
            .sheet(isPresented: $showingCreateUser) {
                CreateUserView(viewModel: viewModel)
                    .environmentObject(sessionManager)
            }
        }
    }
}

struct UserRowView: View {
    let user: User
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(user.username)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(user.email)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct CreateUserView: View {
    @Environment(\.presentationMode) var presentationMode: Binding<PresentationMode>
    @ObservedObject var viewModel: UserAuthViewModel
    @State private var isSubmitting = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("User Information")) {
                    VStack(alignment: .leading, spacing: 8) {
                        TextField("Username", text: $viewModel.username)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)

                        if !viewModel.username.isEmpty {
                            Text("Username: 1+ characters")
                                .font(.caption)
                                .foregroundColor(viewModel.username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? .red : .green)
                        }
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        TextField("Email", text: $viewModel.email)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.emailAddress)
                            .autocapitalization(.none)
                            .disableAutocorrection(true)

                        if !viewModel.email.isEmpty {
                            Text("Email: Valid email address")
                                .font(.caption)
                                .foregroundColor(isValidEmail(viewModel.email) ? .green : .red)
                        }
                    }
                }

                Section {
                    if let errorMessage = viewModel.errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
            }
            .navigationTitle("Create User")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Create") {
                        Task {
                            await createUser()
                        }
                    }
                    .disabled(!viewModel.isFormValid || isSubmitting)
                }
            }
        }
    }

    private func createUser() async {
        isSubmitting = true

        let success = await viewModel.createNewUser()

        isSubmitting = false

        if success {
            presentationMode.wrappedValue.dismiss()
        }
    }

    private func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }
}

#Preview {
    LoginView()
}