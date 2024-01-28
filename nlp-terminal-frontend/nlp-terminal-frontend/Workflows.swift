import SwiftUI
import Foundation

struct Workflows: View {
    var body: some View {
        VStack {
            
            HStack {
                Text("Workflows").bold()
                Spacer()
            }.padding(.leading, 8)
            
            Divider()
            
            VStack {
                SingleWorkflow(workflowName: "Achyut's Work")
            }
        }
        .frame(width: 150)
        .padding(.vertical, 10)
        .padding(.horizontal, 5)
    }
}

struct SingleWorkflow: View {
    var workflowName: String
    @State private var isHovered = false
    
    var body: some View {
        HStack {
            Image(systemName: "cube.transparent")
                .font(Font.system(size: 14))
                .foregroundColor(Color.white)
            Text(workflowName)
                .foregroundColor(Color.white)
            Spacer()
        }
        .padding(.vertical, 4)
        .padding(.horizontal, 8)
        .background(RoundedRectangle(cornerRadius: 6)
                        .fill(isHovered ? Color.gray : Color.clear))
        .onHover { hovering in
            withAnimation {
                self.isHovered = hovering
            }
        }
    }
}


#Preview {
    Workflows()
}
