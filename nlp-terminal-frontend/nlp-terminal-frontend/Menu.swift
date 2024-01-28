import SwiftUI
import Speech

struct Menu: View {
    @State private var userInput: String = ""
    @State private var isRecording: Bool = false
    @State private var isLoading: Bool = false
    @State private var responseText: String = ""

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                CustomTextFieldWithButton(
                    userInput: $userInput,
                    isRecording: $isRecording,
                    submitAction: {
                        handleSubmit(speech: false)
                    },
                    activateMicrophone: {
                        if !isRecording {
                            handleSubmit(speech: true)
                        }
                        isRecording.toggle()
                    }
                )
                .padding(.vertical, 10)
                .background(Color.clear)

                if !responseText.isEmpty {
                    Divider()
                }
                
                if !responseText.isEmpty {
                    ScrollView {
                        Text(responseText)
                            .padding(10)
                            .frame(width: 400, height: 300)
                    }
                }
            }
            .font(.system(size: 16))
            .frame(width: 400, height: responseText.isEmpty ? 55 : 355)
        }
    }

    func handleSubmit(speech: Bool) {
        guard let url = URL(string: "http://127.0.0.1:8000/query") else {
            print("Invalid URL")
            return
        }

        var requestBody: [String: Any] = ["question": userInput]

        requestBody["is_voice"] = speech ? true : false

        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            print("Error encoding JSON data")
            return
        }

        isLoading = true

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                if let error = error {
                    print("Error: \(error)")
                } else if let data = data {
                    if let responseString = String(data: data, encoding: .utf8),
                       let jsonData = responseString.data(using: .utf8),
                       let jsonResponse = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                       let responseDict = jsonResponse["response"] as? [String: Any],
                       let response = responseDict["output"] as? String {
                           responseText = response
                            
                    }
                }
            }
        }
        task.resume()
    }

    func activeMicrophone() {
        print("Active")
    }

    func inactiveMicrophone() {
        print("Inactive")
    }
}

struct CustomTextFieldWithButton: View {
    @Binding var userInput: String
    @Binding var isRecording: Bool
    var submitAction: () -> Void
    var activateMicrophone: () -> Void

    var body: some View {
        TextField("", text: $userInput, prompt: Text("Ask Flow"))
            .frame(height: 35)
            .textFieldStyle(PlainTextFieldStyle())
            .padding([.horizontal], 4)
            .cornerRadius(200)
            .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.clear))
            .padding([.leading], 8)
            .onSubmit {
                if userInput.isEmpty {
                    activateMicrophone()
                } else {
                    submitAction()
                }
                userInput = ""
                
            }
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
                            .font(.system(size: 16))
                            .padding(.trailing, 8)
                    }.buttonStyle(PlainButtonStyle())
                }
            )
        .padding(.trailing, 10)
    }
}

#Preview {
    Menu()
}
