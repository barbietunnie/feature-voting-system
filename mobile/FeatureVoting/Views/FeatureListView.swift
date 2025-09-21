import SwiftUI

struct FeatureListView: View {
    @StateObject private var viewModel = FeatureViewModel()
    @EnvironmentObject var sessionManager: UserSessionManager
    @State private var showingAddFeature = false

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                if viewModel.isLoading && viewModel.features.isEmpty {
                    ProgressView("Loading features...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if viewModel.features.isEmpty && !viewModel.isLoading {
                    EmptyStateView {
                        showingAddFeature = true
                    }
                } else {
                    List {
                        ForEach(viewModel.features) { feature in
                            FeatureRowView(feature: feature, viewModel: viewModel)
                                .listRowInsets(EdgeInsets(top: 4, leading: 16, bottom: 4, trailing: 16))
                                .listRowSeparator(.hidden)
                                .listRowBackground(Color.clear)
                        }

                        if viewModel.hasMorePages {
                            LoadMoreView(isLoading: viewModel.isLoadingMore) {
                                Task {
                                    await viewModel.loadMoreFeatures()
                                }
                            }
                            .listRowInsets(EdgeInsets())
                            .listRowSeparator(.hidden)
                            .listRowBackground(Color.clear)
                        }
                    }
                    .listStyle(PlainListStyle())
                    .refreshable {
                        await viewModel.refreshFeatures()
                    }
                }

                if let errorMessage = viewModel.errorMessage {
                    ErrorBanner(message: errorMessage) {
                        viewModel.clearError()
                    }
                }
            }
            .navigationTitle("Features")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        if let user = sessionManager.currentUser {
                            Text("Logged in as \(user.username)")
                        }
                        Button("Logout", role: .destructive) {
                            sessionManager.logout()
                        }
                    } label: {
                        Image(systemName: "person.circle")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showingAddFeature = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .task {
                await viewModel.loadFeatures()
            }
            .sheet(isPresented: $showingAddFeature) {
                AddFeatureView(viewModel: viewModel)
            }
        }
    }
}

struct FeatureRowView: View {
    let feature: Feature
    let viewModel: FeatureViewModel
    @State private var isPressed = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(feature.title)
                    .font(.headline)
                    .lineLimit(2)

                Text(feature.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }

            HStack {
                HStack(spacing: 4) {
                    Text("\(feature.voteCount)")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(feature.voteCount > 0 ? .blue : .secondary)

                    Text(feature.voteCount == 1 ? "vote" : "votes")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if feature.voteCount > 10 {
                        Image(systemName: "flame.fill")
                            .font(.caption)
                            .foregroundColor(.orange)
                    } else if feature.voteCount > 5 {
                        Image(systemName: "star.fill")
                            .font(.caption)
                            .foregroundColor(.yellow)
                    }
                }

                Spacer()

                VoteButton(
                    feature: feature,
                    isVoted: viewModel.votedFeatures.contains(feature.id),
                    isLoading: viewModel.votingInProgress.contains(feature.id),
                    onVote: {
                        Task {
                            await viewModel.voteForFeature(feature)
                        }
                    },
                    onRemoveVote: {
                        Task {
                            await viewModel.removeVote(from: feature)
                        }
                    }
                )
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 4)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(.systemBackground))
                .shadow(
                    color: .black.opacity(0.05),
                    radius: isPressed ? 1 : 2,
                    x: 0,
                    y: isPressed ? 1 : 2
                )
        )
        .scaleEffect(isPressed ? 0.98 : 1.0)
        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: isPressed)
        .onTapGesture {
            withAnimation(.spring(response: 0.2, dampingFraction: 0.8)) {
                isPressed = true
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                    isPressed = false
                }
            }
        }
    }
}

struct EmptyStateView: View {
    let onAddFeature: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "lightbulb")
                .font(.system(size: 50))
                .foregroundColor(.gray)

            Text("No features yet")
                .font(.title2)
                .fontWeight(.medium)

            Text("Be the first to suggest a feature!")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button("Add Feature") {
                onAddFeature()
            }
            .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}

struct LoadMoreView: View {
    let isLoading: Bool
    let onLoadMore: () -> Void

    var body: some View {
        HStack {
            if isLoading {
                ProgressView()
                    .scaleEffect(0.8)
                Text("Loading more...")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Button("Load More") {
                    onLoadMore()
                }
                .font(.caption)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
    }
}

struct ErrorBanner: View {
    let message: String
    let onDismiss: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.orange)

            Text(message)
                .font(.caption)
                .foregroundColor(.primary)

            Spacer()

            Button("Dismiss") {
                onDismiss()
            }
            .font(.caption)
        }
        .padding()
        .background(Color.orange.opacity(0.1))
        .border(Color.orange.opacity(0.3), width: 1)
    }
}

struct AddFeatureView: View {
    @Environment(\.presentationMode) var presentationMode: Binding<PresentationMode>
    let viewModel: FeatureViewModel

    @State private var title = ""
    @State private var description = ""
    @State private var isSubmitting = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Feature Details")) {
                    TextField("Title", text: $title)
                        .textFieldStyle(RoundedBorderTextFieldStyle())

                    VStack(alignment: .leading) {
                        Text("Description")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        TextEditor(text: $description)
                            .frame(minHeight: 100)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )
                    }
                }

                Section(footer: footerText) {
                    // Footer section for validation info
                }
            }
            .navigationTitle("New Feature")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        Task {
                            await submitFeature()
                        }
                    }
                    .disabled(isSubmitting || !isValid)
                    .opacity(isSubmitting || !isValid ? 0.6 : 1.0)
                    .animation(.easeInOut(duration: 0.2), value: isSubmitting)
                }
            }
        }
    }

    private var isValid: Bool {
        title.trimmingCharacters(in: .whitespacesAndNewlines).count >= 3 &&
        title.count <= 100 &&
        description.trimmingCharacters(in: .whitespacesAndNewlines).count >= 10 &&
        description.count <= 1000
    }

    private var footerText: Text {
        Text("Title: 3-100 characters\nDescription: 10-1000 characters")
            .font(.caption)
            .foregroundColor(.secondary)
    }

    private func submitFeature() async {
        isSubmitting = true

        // Haptic feedback for submission
        let impact = UIImpactFeedbackGenerator(style: .light)
        impact.impactOccurred()

        let success = await viewModel.createFeature(title: title, description: description)

        isSubmitting = false

        if success {
            // Success haptic feedback
            let successFeedback = UINotificationFeedbackGenerator()
            successFeedback.notificationOccurred(.success)

            // Dismiss with slight delay for better UX
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                presentationMode.wrappedValue.dismiss()
            }
        } else {
            // Error haptic feedback
            let errorFeedback = UINotificationFeedbackGenerator()
            errorFeedback.notificationOccurred(.error)
        }
    }
}

#Preview {
    FeatureListView()
}