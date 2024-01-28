import SwiftUI
import Speech

struct Menu: View {
    @State private var userInput: String = ""
    @State private var isRecording: Bool = false

    var body: some View {
        Form {
            Section {
                CustomTextFieldWithButton(userInput: $userInput, isRecording: $isRecording, submitAction: {
                    print("Submit button tapped")
                    // Add your submit action logic here
                }, activateMicrophone: {
                    if isRecording {
                        print("Recording stopped")
                    } else {
                        print("Recording started")
                    }
                    isRecording.toggle()
                })
                .padding(.vertical, 10)
                .background(Color.clear)
            }
        }.font(.system(size: 20))
        .frame(width: 400, height: 50)
        .padding(8)
    }
}

struct CustomTextFieldWithButton: View {
    @Binding var userInput: String
    @Binding var isRecording: Bool
    var submitAction: () -> Void
    var activateMicrophone: () -> Void

    var body: some View {
        TextField("", text: $userInput, prompt: Text("Enter query"))
            .frame(height: 35)
            .textFieldStyle(PlainTextFieldStyle())
            .padding([.horizontal], 4)
            .cornerRadius(200)
            .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.gray))
            .padding([.leading], 8)
            .overlay(
                HStack {
                    Spacer()
                    Button(action: {
                        if userInput.isEmpty {
                            activateMicrophone()
                        } else {
                            submitAction()
                        }
                    }) {
                        Image(systemName: isRecording ? "stop.circle.fill" : (userInput.isEmpty ? "mic.fill" : "paperplane.fill"))
                            .font(.system(size: 12)) // Adjust the font size here
                            .padding(.trailing, 8)
                    }.buttonStyle(PlainButtonStyle())
                }
                .padding(.trailing, 8)
            )
        .padding(.trailing, 10)
    }
}

#Preview {
    Menu()
}
