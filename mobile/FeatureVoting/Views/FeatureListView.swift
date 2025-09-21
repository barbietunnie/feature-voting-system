import SwiftUI

struct FeatureListView: View {
    @StateObject private var viewModel = FeatureViewModel()
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
                        }

                        if viewModel.hasMorePages {
                            LoadMoreView(isLoading: viewModel.isLoadingMore) {
                                Task {
                                    await viewModel.loadMoreFeatures()
                                }
                            }
                        }
                    }
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
                Text("\(feature.voteCount) votes")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                HStack(spacing: 8) {
                    if viewModel.votingInProgress.contains(feature.id) {
                        ProgressView()
                            .scaleEffect(0.8)
                    } else if viewModel.votedFeatures.contains(feature.id) {
                        Button(action: {
                            Task {
                                await viewModel.removeVote(from: feature)
                            }
                        }) {
                            Image(systemName: "heart.fill")
                                .foregroundColor(.red)
                        }
                    } else {
                        Button(action: {
                            Task {
                                await viewModel.voteForFeature(feature)
                            }
                        }) {
                            Image(systemName: "heart")
                                .foregroundColor(.gray)
                        }
                    }
                }
            }
        }
        .padding(.vertical, 4)
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

        let success = await viewModel.createFeature(title: title, description: description)

        isSubmitting = false

        if success {
            presentationMode.wrappedValue.dismiss()
        }
    }
}

#Preview {
    FeatureListView()
}