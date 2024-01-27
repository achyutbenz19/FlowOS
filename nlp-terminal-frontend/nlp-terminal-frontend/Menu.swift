import Foundation
import SwiftUI
import Speech

struct Menu: View {
    @State private var userInput: String = ""
    
    var body: some View {
        Form {
            Section {
                TextField("", text: $userInput, prompt: Text("Enter query"))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }.padding(.bottom, 3)
            Section {
                HStack {
                    
                    Button(action: {
                        submitAction()
                    }) {
                        Image(systemName: "paperplane.fill")
                    }
                    
                    Button(action: {
                        activateMicrophone()
                    }) {
                        Image(systemName: "mic.fill")
                    }
                    
                }
            }
        }.padding(.vertical, 10).padding(.trailing, 8)
    }
    
    func submitAction() {
        print(userInput)
    }
    
    func activateMicrophone() {
        print("Microphone Activated!")
    }
    
}

#Preview {
    Menu()
}
