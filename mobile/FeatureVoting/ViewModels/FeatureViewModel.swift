import Foundation

@MainActor
class FeatureViewModel: ObservableObject {
    @Published var features: [Feature] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService()

    func loadFeatures() async {
        isLoading = true
        errorMessage = nil

        do {
            features = try await apiService.fetchFeatures()
        } catch {
            errorMessage = "Failed to load features: \(error.localizedDescription)"
        }

        isLoading = false
    }

    func createFeature(title: String, description: String) async {
        let newFeature = FeatureCreate(title: title, description: description)

        do {
            let createdFeature = try await apiService.createFeature(newFeature)
            features.append(createdFeature)
        } catch {
            errorMessage = "Failed to create feature: \(error.localizedDescription)"
        }
    }

    func vote(on feature: Feature, isUpvote: Bool) async {
        let vote = VoteCreate(featureId: feature.id, isUpvote: isUpvote)

        do {
            _ = try await apiService.createVote(vote)
            await loadFeatures()
        } catch {
            errorMessage = "Failed to vote: \(error.localizedDescription)"
        }
    }
}