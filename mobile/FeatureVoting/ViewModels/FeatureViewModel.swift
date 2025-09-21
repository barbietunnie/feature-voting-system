import Foundation

@MainActor
class FeatureViewModel: ObservableObject {
    @Published var features: [Feature] = []
    @Published var isLoading = false
    @Published var isLoadingMore = false
    @Published var errorMessage: String?
    @Published var currentPage = 1
    @Published var hasMorePages = false
    @Published var totalCount = 0

    private let apiService = APIService()
    private let pageSize = 20

    // Track votes to show immediate feedback
    @Published var votedFeatures: Set<Int> = []
    @Published var votingInProgress: Set<Int> = []

    func loadFeatures(refresh: Bool = false) async {
        if refresh {
            currentPage = 1
            features = []
        }

        isLoading = !refresh && features.isEmpty
        isLoadingMore = !refresh && !features.isEmpty
        errorMessage = nil

        do {
            let pagination = PaginationParams(page: currentPage, pageSize: pageSize)
            let response = try await apiService.fetchFeatures(pagination: pagination)

            if refresh {
                features = response.items
            } else {
                features.append(contentsOf: response.items)
            }

            totalCount = response.totalCount
            hasMorePages = response.hasNext

            if hasMorePages {
                currentPage += 1
            }
        } catch {
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
            } else {
                errorMessage = "Failed to load features: \(error.localizedDescription)"
            }
            if AppConfig.isDebugMode {
                print("Error loading features: \(error)")
            }
        }

        isLoading = false
        isLoadingMore = false
    }

    func loadMoreFeatures() async {
        guard hasMorePages && !isLoadingMore else { return }
        await loadFeatures(refresh: false)
    }

    func refreshFeatures() async {
        await loadFeatures(refresh: true)
    }

    func createFeature(title: String, description: String) async -> Bool {
        guard !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              !description.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "Title and description cannot be empty"
            return false
        }

        guard title.count >= 3 && title.count <= 100 else {
            errorMessage = "Title must be between 3 and 100 characters"
            return false
        }

        guard description.count >= 10 && description.count <= 1000 else {
            errorMessage = "Description must be between 10 and 1000 characters"
            return false
        }

        errorMessage = nil
        let newFeature = FeatureCreate(
            title: title.trimmingCharacters(in: .whitespacesAndNewlines),
            description: description.trimmingCharacters(in: .whitespacesAndNewlines)
        )

        do {
            let createdFeature = try await apiService.createFeature(newFeature)
            // Insert at beginning since features are sorted by vote count
            features.insert(createdFeature, at: 0)
            return true
        } catch {
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
            } else {
                errorMessage = "Failed to create feature: \(error.localizedDescription)"
            }
            if AppConfig.isDebugMode {
                print("Error creating feature: \(error)")
            }
            return false
        }
    }

    func voteForFeature(_ feature: Feature) async {
        guard !votingInProgress.contains(feature.id) else { return }
        guard !votedFeatures.contains(feature.id) else {
            errorMessage = "You have already voted for this feature"
            return
        }

        votingInProgress.insert(feature.id)
        errorMessage = nil

        do {
            let response = try await apiService.voteForFeature(featureId: feature.id)
            votedFeatures.insert(feature.id)

            // Update the feature in the list
            if let index = features.firstIndex(where: { $0.id == feature.id }) {
                let updatedFeature = Feature(
                    id: feature.id,
                    title: feature.title,
                    description: feature.description,
                    authorId: feature.authorId,
                    createdAt: feature.createdAt,
                    voteCount: response.voteCount
                )
                features[index] = updatedFeature

                // Re-sort the features since vote count changed
                sortFeatures()
            }
        } catch {
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
            } else {
                errorMessage = "Failed to vote: \(error.localizedDescription)"
            }
            if AppConfig.isDebugMode {
                print("Error voting for feature: \(error)")
            }
        }

        votingInProgress.remove(feature.id)
    }

    func removeVote(from feature: Feature) async {
        guard !votingInProgress.contains(feature.id) else { return }
        guard votedFeatures.contains(feature.id) else {
            errorMessage = "You haven't voted for this feature"
            return
        }

        votingInProgress.insert(feature.id)
        errorMessage = nil

        do {
            let response = try await apiService.removeVote(featureId: feature.id)
            votedFeatures.remove(feature.id)

            // Update the feature in the list
            if let index = features.firstIndex(where: { $0.id == feature.id }) {
                let updatedFeature = Feature(
                    id: feature.id,
                    title: feature.title,
                    description: feature.description,
                    authorId: feature.authorId,
                    createdAt: feature.createdAt,
                    voteCount: response.voteCount
                )
                features[index] = updatedFeature

                // Re-sort the features since vote count changed
                sortFeatures()
            }
        } catch {
            if let apiError = error as? APIError {
                errorMessage = apiError.userFriendlyMessage
                if case .notFound = apiError {
                    votedFeatures.remove(feature.id)
                }
            } else {
                errorMessage = "Failed to remove vote: \(error.localizedDescription)"
            }
            if AppConfig.isDebugMode {
                print("Error removing vote: \(error)")
            }
        }

        votingInProgress.remove(feature.id)
    }

    func clearError() {
        errorMessage = nil
    }

    private func sortFeatures() {
        features.sort { $0.voteCount > $1.voteCount }
    }
}