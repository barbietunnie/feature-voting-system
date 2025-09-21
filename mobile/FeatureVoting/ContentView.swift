import SwiftUI

struct ContentView: View {
    @StateObject private var sessionManager = UserSessionManager()

    var body: some View {
        Group {
            if sessionManager.isLoggedIn {
                FeatureListView()
                    .environmentObject(sessionManager)
            } else {
                LoginView()
                    .environmentObject(sessionManager)
            }
        }
    }
}

#Preview {
    ContentView()
}