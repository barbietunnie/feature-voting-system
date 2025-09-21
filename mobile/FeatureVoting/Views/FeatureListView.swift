import SwiftUI

struct FeatureListView: View {
    @StateObject private var viewModel = FeatureViewModel()

    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    ProgressView("Loading features...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if viewModel.features.isEmpty {
                    Text("No features available")
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(viewModel.features) { feature in
                        FeatureRowView(feature: feature, viewModel: viewModel)
                    }
                }

                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .padding()
                }
            }
            .navigationTitle("Features")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Add") {
                        // TODO: Present add feature sheet
                    }
                }
            }
            .task {
                await viewModel.loadFeatures()
            }
        }
    }
}

struct FeatureRowView: View {
    let feature: Feature
    let viewModel: FeatureViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(feature.title)
                .font(.headline)

            Text(feature.description)
                .font(.body)
                .foregroundColor(.secondary)

            HStack {
                Text(feature.status.displayName)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(statusColor.opacity(0.2))
                    .foregroundColor(statusColor)
                    .cornerRadius(8)

                Spacer()

                HStack {
                    Button(action: {
                        Task {
                            await viewModel.vote(on: feature, isUpvote: true)
                        }
                    }) {
                        Image(systemName: "arrow.up")
                    }

                    Text("\(feature.voteCount ?? 0)")

                    Button(action: {
                        Task {
                            await viewModel.vote(on: feature, isUpvote: false)
                        }
                    }) {
                        Image(systemName: "arrow.down")
                    }
                }
            }
        }
        .padding(.vertical, 4)
    }

    private var statusColor: Color {
        switch feature.status {
        case .pending: return .orange
        case .inProgress: return .blue
        case .completed: return .green
        case .rejected: return .red
        }
    }
}

#Preview {
    FeatureListView()
}