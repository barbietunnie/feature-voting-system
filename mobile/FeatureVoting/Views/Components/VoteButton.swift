import SwiftUI

struct VoteButton: View {
    let feature: Feature
    let isVoted: Bool
    let isLoading: Bool
    let onVote: () -> Void
    let onRemoveVote: () -> Void

    @State private var isPressed = false
    @State private var showVoteAnimation = false

    var body: some View {
        Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                isPressed = true
            }

            // Haptic feedback
            let impact = UIImpactFeedbackGenerator(style: .medium)
            impact.impactOccurred()

            if isVoted {
                onRemoveVote()
            } else {
                onVote()
                withAnimation(.spring(response: 0.5, dampingFraction: 0.8).delay(0.1)) {
                    showVoteAnimation = true
                }
            }

            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                    isPressed = false
                }
            }

            if showVoteAnimation {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
                    showVoteAnimation = false
                }
            }
        }) {
            ZStack {
                if isLoading {
                    ProgressView()
                        .scaleEffect(0.8)
                        .frame(width: 24, height: 24)
                } else {
                    Image(systemName: isVoted ? "heart.fill" : "heart")
                        .font(.system(size: 18, weight: .medium))
                        .foregroundColor(isVoted ? .red : .gray)
                        .scaleEffect(isPressed ? 1.3 : 1.0)
                        .scaleEffect(showVoteAnimation ? 1.4 : 1.0)
                        .opacity(showVoteAnimation ? 0.8 : 1.0)
                }

                // Animated particles for vote feedback
                if showVoteAnimation && !isVoted {
                    ForEach(0..<6, id: \.self) { index in
                        Image(systemName: "heart.fill")
                            .font(.system(size: 8))
                            .foregroundColor(.red.opacity(0.7))
                            .offset(
                                x: cos(Double(index) * .pi / 3) * 20,
                                y: sin(Double(index) * .pi / 3) * 20
                            )
                            .scaleEffect(showVoteAnimation ? 0.1 : 0.8)
                            .opacity(showVoteAnimation ? 0 : 1)
                            .animation(
                                .easeOut(duration: 0.6).delay(0.1),
                                value: showVoteAnimation
                            )
                    }
                }
            }
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(isLoading)
    }
}

#Preview {
    HStack(spacing: 20) {
        VoteButton(
            feature: Feature(
                id: 1,
                title: "Test Feature",
                description: "Test Description",
                authorId: 1,
                createdAt: Date(),
                voteCount: 5
            ),
            isVoted: false,
            isLoading: false,
            onVote: {},
            onRemoveVote: {}
        )

        VoteButton(
            feature: Feature(
                id: 2,
                title: "Test Feature",
                description: "Test Description",
                authorId: 1,
                createdAt: Date(),
                voteCount: 5
            ),
            isVoted: true,
            isLoading: false,
            onVote: {},
            onRemoveVote: {}
        )

        VoteButton(
            feature: Feature(
                id: 3,
                title: "Test Feature",
                description: "Test Description",
                authorId: 1,
                createdAt: Date(),
                voteCount: 5
            ),
            isVoted: false,
            isLoading: true,
            onVote: {},
            onRemoveVote: {}
        )
    }
    .padding()
}