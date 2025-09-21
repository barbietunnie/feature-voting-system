# Feature Voting System - iOS App

Native iOS application built with SwiftUI, featuring a modern user interface, comprehensive error handling, and seamless API integration.

## 📱 iOS Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SwiftUI       │    │   ViewModels    │    │   API Service   │
│   Views         │────┤   (MVVM)        │────┤   (URLSession)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Models        │    │   Session       │    │   FastAPI       │
│   (Codable)     │    │   Manager       │    │   Backend       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Setup

### Prerequisites
- **Xcode 15.0+** (recommended latest version)
- **macOS 13.0+** (Ventura or later)
- **iOS 16.0+** deployment target
- **Swift 5.9+**

### 1. Development Environment
```bash
# Check Xcode version
xcodebuild -version

# Install Xcode Command Line Tools (if needed)
xcode-select --install

# Verify Swift version
swift --version
```

### 2. Project Setup
```bash
# Navigate to mobile directory
cd mobile

# Open Xcode project
open FeatureVoting.xcodeproj

# Or use Xcode command line
xed .
```

### 3. Configuration
Before running the app, ensure the backend API is running at `http://localhost:8000`

The app automatically configures the API endpoint based on build configuration:
- **Debug**: `http://localhost:8000/api`
- **Staging**: `https://staging-api.featurevoting.com/api`
- **Release**: `https://api.featurevoting.com/api`

### 4. Build and Run
1. Select a simulator or connected device
2. Press `⌘+R` to build and run
3. The app will launch and connect to your local backend

## 📁 Project Structure

```
mobile/
├── README.md                          # This file
├── FeatureVoting.xcodeproj/          # Xcode project
└── FeatureVoting/                    # App source code
    ├── FeatureVotingApp.swift       # App entry point
    ├── ContentView.swift            # Main content view
    ├── Config/                      # Configuration
    │   └── Environment.swift        # Environment settings
    ├── Models/                      # Data models
    │   ├── User.swift              # User model
    │   ├── Feature.swift           # Feature model
    │   ├── Vote.swift              # Vote model
    │   └── PaginatedResponse.swift  # Pagination model
    ├── ViewModels/                 # MVVM ViewModels
    │   ├── UserAuthViewModel.swift  # User authentication
    │   └── FeatureViewModel.swift   # Feature management
    ├── Views/                      # SwiftUI Views
    │   ├── LoginView.swift         # User login/creation
    │   ├── FeatureListView.swift   # Feature list and voting
    │   └── Components/             # Reusable components
    │       └── VoteButton.swift    # Custom vote button
    └── Services/                   # Service layer
        ├── APIService.swift        # API communication
        └── UserSessionManager.swift # User session management
```

## 🛠️ Development

### Building the Project

#### Using Xcode
1. Open `FeatureVoting.xcodeproj`
2. Select target device/simulator
3. Product → Build (`⌘+B`)
4. Product → Run (`⌘+R`)

#### Using Command Line
```bash
# Build for simulator
xcodebuild -project FeatureVoting.xcodeproj -scheme FeatureVoting -sdk iphonesimulator

# Build for device
xcodebuild -project FeatureVoting.xcodeproj -scheme FeatureVoting -sdk iphoneos

# Clean build folder
xcodebuild clean -project FeatureVoting.xcodeproj -scheme FeatureVoting
```

### Running on Different Targets

#### iOS Simulator
- **Recommended**: iPhone 15 Pro (iOS 17.0+)
- **Minimum**: iPhone SE (3rd generation) (iOS 16.0+)
- All iPad models supported

#### Physical Device
1. Connect iPhone/iPad via USB
2. Trust the development certificate
3. Select device in Xcode
4. Build and run

### Architecture Patterns

#### MVVM (Model-View-ViewModel)
```swift
// View observes ViewModel
struct FeatureListView: View {
    @StateObject private var viewModel = FeatureViewModel()

    var body: some View {
        // UI bound to viewModel properties
        List(viewModel.features) { feature in
            FeatureRowView(feature: feature)
        }
    }
}

// ViewModel manages business logic
@MainActor
class FeatureViewModel: ObservableObject {
    @Published var features: [Feature] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService()

    func loadFeatures() async {
        // Business logic here
    }
}
```

#### Dependency Injection
```swift
// Services injected via environment
struct FeatureListView: View {
    @EnvironmentObject var sessionManager: UserSessionManager

    var body: some View {
        // Access session manager throughout the view hierarchy
    }
}
```

## 🔧 Configuration

### Environment Settings
The app supports multiple environments configured in `Config/Environment.swift`:

```swift
enum AppEnvironment {
    case development    // Local development
    case staging       // Testing environment
    case production    // Production release
}
```

#### Development Configuration
```swift
case .development:
    return "http://localhost:8000"     // API Base URL
    return 30.0                        // Network timeout
    return true                        // Debug mode
```

#### Build Configurations
- **Debug**: Development settings, verbose logging
- **Staging**: Pre-production testing
- **Release**: Production optimizations, minimal logging

### API Configuration
Update API endpoints in `Config/Environment.swift`:
```swift
var apiBaseURL: String {
    switch self {
    case .development:
        return "http://localhost:8000"
    case .staging:
        return "https://staging-api.yourdomain.com"
    case .production:
        return "https://api.yourdomain.com"
    }
}
```

## 🎨 User Interface

### Design System
The app follows Apple's Human Interface Guidelines with custom enhancements:

#### Color Scheme
- **Primary**: System Blue
- **Secondary**: System Gray
- **Success**: System Green
- **Error**: System Red
- **Warning**: System Orange

#### Typography
- **Headlines**: San Francisco Bold
- **Body**: San Francisco Regular
- **Captions**: San Francisco Light

#### Components
- **Custom Vote Button**: Animated voting interaction
- **Error Banner**: Contextual error messaging
- **Loading States**: Smooth progress indicators

### Accessibility
- **Dynamic Type**: Supports all accessibility text sizes
- **Voice Over**: Full screen reader support
- **High Contrast**: Adapts to accessibility settings
- **Reduced Motion**: Respects motion preferences

## 📱 Features

### User Management
- **User Selection**: Choose from existing users
- **User Creation**: Create new user profiles
- **Form Validation**: Real-time input validation
- **Error Handling**: User-friendly error messages

### Feature Voting
- **Feature List**: Paginated list of all features
- **Vote/Unvote**: Toggle votes with immediate feedback
- **Vote Counts**: Real-time vote count updates
- **Feature Creation**: Submit new feature requests

### Network Handling
- **Offline Support**: Graceful offline state handling
- **Retry Logic**: Automatic retry for failed requests
- **Loading States**: Clear loading indicators
- **Error Recovery**: Smart error recovery options

## 🧪 Testing

### Unit Testing
```bash
# Run tests from Xcode
⌘+U

# Or using command line
xcodebuild test -project FeatureVoting.xcodeproj -scheme FeatureVoting -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

### UI Testing
```swift
// Example UI test
func testFeatureListLoading() {
    let app = XCUIApplication()
    app.launch()

    // Wait for features to load
    let featuresList = app.tables["FeaturesList"]
    XCTAssertTrue(featuresList.waitForExistence(timeout: 5))
}
```

### Test Coverage
- **ViewModels**: Business logic testing
- **API Service**: Network request/response testing
- **UI Components**: User interaction testing
- **Error Handling**: Error state validation

## 🚀 Deployment

### Development Builds
Automatic signing with development team:
1. Select your Apple Developer account in Xcode
2. Choose automatic signing
3. Build and run on device

### TestFlight Distribution
1. Archive the build (`Product → Archive`)
2. Upload to App Store Connect
3. Add to TestFlight
4. Invite internal/external testers

### App Store Release
1. Create app record in App Store Connect
2. Upload build via Xcode or Transporter
3. Submit for review
4. Release to App Store

### Build Configurations
```bash
# Debug build (development)
xcodebuild -configuration Debug

# Release build (production)
xcodebuild -configuration Release
```

## 🔍 Debugging

### Xcode Debugging
- **Breakpoints**: Set breakpoints in Swift code
- **LLDB**: Use LLDB debugger commands
- **Memory Graph**: Debug memory leaks
- **View Hierarchy**: Inspect UI layout

### Network Debugging
```swift
// Enable network logging (Debug builds only)
#if DEBUG
print("API Request: \(request.url?.absoluteString ?? "")")
print("Response: \(String(data: data, encoding: .utf8) ?? "")")
#endif
```

### Console Logging
```swift
// Structured logging
if AppConfig.isDebugMode {
    print("🌐 [API] Fetching features...")
    print("✅ [API] Successfully loaded \(features.count) features")
    print("❌ [ERROR] Failed to load features: \(error)")
}
```

## 🔧 Performance Optimization

### Memory Management
- **Weak References**: Prevent retain cycles
- **Lazy Loading**: Load data on demand
- **Image Caching**: Efficient image handling
- **Background Tasks**: Proper background processing

### Network Optimization
- **Request Debouncing**: Prevent excessive API calls
- **Response Caching**: Cache appropriate responses
- **Connection Pooling**: Reuse network connections
- **Timeout Configuration**: Appropriate timeout values

### UI Performance
- **List Virtualization**: Efficient large list rendering
- **Animation Optimization**: Smooth 60fps animations
- **Image Compression**: Optimized image sizes
- **View Recycling**: Proper view lifecycle management

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clean build folder
⌘+Shift+K

# Clean derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reset simulator
xcrun simctl erase all
```

#### Network Issues
- Ensure backend is running on `http://localhost:8000`
- Check iOS simulator network settings
- Verify API endpoints in Environment.swift

#### Code Signing Issues
- Check Apple Developer account status
- Verify provisioning profiles
- Update bundle identifier if needed

### Performance Issues
- Use Instruments to profile performance
- Check for retain cycles with Memory Graph
- Monitor network requests in Network tab

## 📊 Analytics and Monitoring

### Built-in Metrics
- **API Response Times**: Tracked in APIService
- **Error Rates**: Logged for debugging
- **User Actions**: Basic interaction tracking
- **Crash Reporting**: Xcode crash logs

### Future Enhancements
- **Firebase Analytics**: User behavior tracking
- **Crashlytics**: Advanced crash reporting
- **Performance Monitoring**: Real-time performance data

## 🤝 Contributing

### Code Style
- Follow Swift API Design Guidelines
- Use SwiftLint for style consistency
- Maintain MVVM architecture patterns
- Add comprehensive comments for complex logic

### Pull Request Process
1. Create feature branch from main
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Submit pull request with description

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-voting-ui

# Make changes and commit
git add .
git commit -m "Add enhanced voting UI with animations"

# Push and create PR
git push origin feature/new-voting-ui
```

---

For complete project documentation, see the [main README.md](../README.md).