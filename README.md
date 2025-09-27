# REVLINE - AI Fitness Assistant 💪

A futuristic fitness chatbot with modern UI, conversation memory, and intelligent context awareness. REVLINE is your dedicated AI fitness assistant that helps with workouts, nutrition, wellness guidance, and document analysis.

## 🚀 Features

### 🎯 **Intelligent Fitness Assistant**
- **Specialized Knowledge**: Focuses exclusively on fitness, nutrition, and wellness topics
- **Conversation Memory**: Maintains context throughout conversations for personalized responses
- **Context Awareness**: Understands follow-up questions and contextual responses
- **Positive Feedback Recognition**: Acknowledges user appreciation and provides motivational responses

### 💪 **Comprehensive Workout Plans**
- **Muscle Group Specific**: Detailed workouts for chest, back, legs, shoulders, arms, and core
- **Fitness Level Adaptation**: Beginner, intermediate, and advanced programs
- **Home & Gym Variants**: Bodyweight and equipment-based exercise options
- **Quick Workouts**: 10-minute HIIT routines for busy schedules

### 🎨 **Modern UI & Experience**
- **Futuristic Design**: Dark/light theme toggle with smooth animations
- **Responsive Interface**: Works perfectly on desktop and mobile devices
- **Custom Animations**: Fade-in effects, glowing elements, and smooth transitions
- **Document Chat**: Upload and analyze fitness-related PDFs and documents

### 🧠 **Advanced Context Intelligence**
- **Topic Validation**: Automatically filters non-fitness topics
- **Smart Follow-ups**: Understands contextual responses like "home", "average", "beginner"
- **Memory Persistence**: Remembers previous discussions for better continuity
- **Feedback Recognition**: Responds appropriately to positive feedback and encouragement

## 🛠 **Technology Stack**

### **Frontend**
- **React + TypeScript**: Modern component-based architecture
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Animations**: CSS keyframes for futuristic effects

### **Backend**
- **FastAPI**: High-performance Python web framework
- **CORS Middleware**: Cross-origin resource sharing support
- **Context Management**: Conversation memory and state management
- **Document Processing**: PDF upload and analysis capabilities

## 📁 **Project Structure**

```
fitness chatbot/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── index.css        # Custom styles and animations
│   │   └── main.tsx         # Application entry point
│   ├── package.json         # Frontend dependencies
│   └── vite.config.ts       # Vite configuration
├── test_server.py           # FastAPI backend server
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 16+ and npm/yarn
- Python 3.8+ and pip
- Modern web browser

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/RohithDharshan/FitnessChatBot.git
   cd fitness\ chatbot
   ```

2. **Setup Backend**
   ```bash
   pip install -r requirements.txt
   python test_server.py
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 🎯 **Usage Examples**

### **Basic Fitness Queries**
- "Create a 10 min workout plan" → Get instant HIIT routine
- "chest" → Detailed chest workout with exercises and tips
- "home" (after muscle discussion) → Bodyweight alternatives

### **Contextual Conversations**
- "What's your fitness level?" → "Average" → Personalized intermediate plan
- "legs" → "home" → Home leg workout with bodyweight exercises
- "good job" → Motivational fitness-focused response

### **Document Analysis**
- Upload fitness PDFs → Ask questions about the content
- Non-fitness documents → Polite redirection to fitness topics

## 🏗 **Architecture**

### **Conversation Flow**
1. **Input Validation**: Checks if query is fitness-related
2. **Context Analysis**: Examines recent conversation history
3. **Response Generation**: Creates appropriate fitness guidance
4. **Memory Update**: Stores conversation context for future reference

### **Key Components**
- **Theme Context**: Manages dark/light mode preferences
- **Chat Interface**: Handles user interactions and message display
- **Backend API**: Processes queries and maintains conversation state
- **Document Processor**: Analyzes uploaded fitness documents

## 👥 **Team Members**

- **23N241** - Rohith Dharshan M
- **23N232** - Nikileshh S  
- **23N230** - Murali Karthik S
- **23N203** - Aakash Balaa Sivakumar
- **23N248** - Sanjeev MS
- **23Z348** - NV Sri Ram

## 🎨 **Design Philosophy**

REVLINE combines cutting-edge AI technology with a user-centric design approach:

- **Fitness-First**: Every feature is designed around fitness and wellness
- **Context Intelligence**: Understands user intent beyond keywords
- **Visual Excellence**: Modern, futuristic UI that enhances user experience
- **Accessibility**: Works across devices and user preferences
- **Performance**: Fast, responsive interactions with smooth animations

## 🔮 **Future Enhancements**

- **Workout Tracking**: Log and monitor fitness progress
- **Nutrition Calculator**: Macro and calorie counting tools
- **Video Integration**: Exercise demonstration videos
- **Social Features**: Share workouts and connect with fitness community
- **Wearable Integration**: Connect with fitness trackers and smartwatches
- **AI Coaching**: Personalized training programs with progress adaptation

## 🤝 **Contributing**

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests to help improve REVLINE.

## 📄 **License**

This project is developed as part of an academic assignment. All rights reserved.

---

**REVLINE** - Your AI-powered fitness journey starts here! 💪🚀