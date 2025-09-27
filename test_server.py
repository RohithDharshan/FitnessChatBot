from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

app = FastAPI(title="REVLINE Test Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (in production, use a database)
conversations: Dict[str, List[Dict]] = {}

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class RAGRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "REVLINE Fitness Chatbot Server is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with fitness topic validation and conversation memory"""
    
    # Get the conversation context (last few messages)
    conversation_context = [msg.content for msg in request.messages[-5:]]  # Last 5 messages for context
    current_message = request.messages[-1].content if request.messages else ""
    
    # Enhanced fitness-related keywords for validation
    fitness_keywords = [
        "workout", "exercise", "fitness", "gym", "training", "muscle", "strength", "cardio", 
        "running", "jogging", "swimming", "cycling", "yoga", "pilates", "weightlifting",
        "nutrition", "diet", "protein", "carbs", "calories", "weight", "fat", "lean",
        "health", "wellness", "recovery", "rest", "sleep", "stretching", "flexibility",
        "bodybuilding", "crossfit", "hiit", "endurance", "sports", "athletic", "physique",
        "supplements", "vitamins", "hydration", "water", "meal", "food", "eating",
        "bulk", "cut", "shred", "tone", "abs", "biceps", "triceps", "legs", "chest",
        "back", "shoulders", "core", "squat", "deadlift", "benchpress", "pushup",
        "pullup", "plank", "burpee", "lunge", "crunch", "situp", "dumbbell", "barbell",
        "hi", "hello", "hey", "revline", "help", "advice", "assistant", "plan",
        # Muscle groups and body parts
        "pecs", "pectorals", "delts", "deltoids", "lats", "latissimus", "traps", "trapezius",
        "rhomboids", "erector", "spine", "glutes", "gluteus", "hamstrings", "quadriceps",
        "quads", "calves", "gastrocnemius", "soleus", "forearms", "bicep", "tricep",
        # Exercise variations
        "incline", "decline", "flat", "dumbbell", "barbell", "cable", "machine",
        "isolation", "compound", "unilateral", "bilateral", "superset", "circuit",
        # Workout types
        "hiit", "tabata", "emom", "amrap", "wod", "circuit", "interval", "steady",
        "tempo", "pause", "drop", "pyramid", "ladder", "cluster", "rest",
        # Time and numbers
        "10", "min", "minute", "minutes", "second", "seconds", "hour", "hours",
        "reps", "repetitions", "sets", "rounds", "cycles", "time", "duration",
        # Context-aware keywords
        "beginner", "intermediate", "advanced", "average", "level", "experience",
        "start", "starting", "begin", "beginning", "new", "first", "time",
        "more", "less", "increase", "decrease", "better", "improve", "progress",
        "yes", "no", "okay", "sure", "thanks", "thank you", "great", "good",
        # Location and equipment contexts
        "home", "house", "bedroom", "living", "room", "apartment", "indoor",
        "outdoor", "park", "outside", "gym", "equipment", "no equipment",
        "bodyweight", "minimal", "simple", "basic", "easy", "hard", "harder",
        "variations", "alternatives", "options", "different", "modify", "change"
    ]
    
    # Fitness context indicators in conversation history
    fitness_context_keywords = [
        "workout", "exercise", "fitness", "gym", "training", "muscle", "strength",
        "nutrition", "diet", "weight", "health", "wellness", "level", "plan",
        "revline", "fitness assistant", "specialized fitness", "analyze fitness",
        "fitness content", "wellness content", "exercise content", "nutrition content"
    ]
    
    def has_fitness_context(conversation):
        """Check if recent conversation has fitness context"""
        recent_text = " ".join(conversation).lower()
        return any(keyword in recent_text for keyword in fitness_context_keywords)
    
    def is_fitness_related(text, has_context=False):
        """Check if the message is fitness-related, considering conversation context"""
        text_lower = text.lower()
        
        # Direct fitness keywords
        if any(keyword in text_lower for keyword in fitness_keywords):
            return True
        
        # If we have fitness context, allow contextual responses and feedback
        if has_context:
            contextual_words = [
                # Contextual responses
                "average", "beginner", "intermediate", "advanced", "basic", "simple",
                "more", "less", "increase", "decrease", "better", "improve", "change",
                "yes", "no", "okay", "sure", "continue", "next", "then", "also", 
                "what about", "how about", "tell me", "show me", "give me", 
                "can you", "will you", "should i",
                # Positive feedback and encouragement (fitness context)
                "thanks", "thank you", "great", "good", "perfect", "awesome",
                "excellent", "amazing", "fantastic", "wonderful", "nice",
                "good job", "well done", "impressive", "helpful", "useful",
                "love it", "like it", "cool", "wow", "nice work", "appreciate",
                # Location and equipment
                "home", "house", "apartment", "gym", "equipment", "bodyweight",
                "variations", "alternatives", "options", "modify", "different"
            ]
            if any(word in text_lower for word in contextual_words):
                return True
        
        # Reject clearly non-fitness topics even with context
        non_fitness_topics = [
            "programming", "coding", "software", "computer", "technology",
            "politics", "religion", "weather", "news", "movies", "music",
            "cooking" , "recipe", "travel", "business", "finance", "money",
            "school", "education", "history", "science", "math", "literature"
        ]
        
        # Only reject if it's clearly about non-fitness topics
        if any(topic in text_lower for topic in non_fitness_topics):
            return False
        
        return False
    
    # Check conversation context
    has_context = has_fitness_context(conversation_context)
    
    # Check if the question is fitness-related
    if not is_fitness_related(current_message, has_context):
        return {
            "response": {
                "role": "assistant",
                "content": "I'm REVLINE, a specialized fitness assistant. I can only help with fitness, exercise, nutrition, and wellness topics. Please ask me something related to your health and fitness journey! 💪🏋️‍♂️"
            }
        }
    
    # Context-aware responses based on conversation history
    user_lower = current_message.lower()
    
    # Check for home/equipment context in recent conversation
    recent_context = " ".join(conversation_context[-3:]).lower()  # Last 3 messages
    
    # Check for positive feedback/encouragement in fitness context
    if any(word in user_lower for word in [
        "good job", "great job", "well done", "thanks", "thank you", "great", 
        "good", "perfect", "awesome", "excellent", "amazing", "fantastic", 
        "wonderful", "nice", "helpful", "useful", "love it", "like it", 
        "cool", "wow", "appreciate", "good response", "great response",
        "nice work", "well said", "correct", "right", "exactly"
    ]):
        # Check if we're in any REVLINE context (fitness responses or document rejections)
        revline_context = any(phrase in recent_context for phrase in [
            "revline", "fitness assistant", "specialized fitness", "only help",
            "fitness, exercise, nutrition", "wellness", "workout", "training"
        ])
        
        if has_context or revline_context:
            positive_responses = [
                "Thank you! 💪 I'm REVLINE, your dedicated fitness assistant. Ready to help with any fitness, nutrition, or wellness questions!",
                "Appreciate the feedback! 🚀 I'm here to keep you focused on your fitness goals. What fitness topic interests you?",
                "Thanks! 🔥 I stay committed to fitness topics only - it helps me give you the best workout and nutrition advice! What's next?",
                "Glad you understand! 🎯 I'm specialized in fitness to provide you with expert guidance. Ready for some fitness discussion?",
                "You got it! 💪 I'm your fitness-focused AI. Let's talk workouts, nutrition, or wellness - what's on your mind?",
                "Exactly! 🌟 I keep our conversations fitness-focused so I can be your best training partner. What fitness topic can I help with?"
            ]
            import random
            return {
                "response": {
                    "role": "assistant",
                    "content": random.choice(positive_responses)
                }
            }
    
    # Home workout variations based on previous muscle group discussion
    if any(word in user_lower for word in ["home", "house", "apartment", "no equipment", "bodyweight"]) and has_context:
        if any(muscle in recent_context for muscle in ["chest", "pec"]):
            return {
                "response": {
                    "role": "assistant",
                    "content": "🏠 **HOME CHEST WORKOUT** - No equipment needed!\n\n💪 **Bodyweight Chest Exercises**:\n• **Push-ups**: 3-4 sets x 8-15 reps (adjust difficulty as needed)\n• **Incline Push-ups**: 3 sets x 10-12 reps (hands on couch/chair)\n• **Decline Push-ups**: 3 sets x 6-10 reps (feet elevated)\n• **Wide-Grip Push-ups**: 2 sets x 8-12 reps (targets outer chest)\n\n🎯 **Push-up Progressions**:\n• **Beginner**: Wall push-ups → Knee push-ups → Full push-ups\n• **Advanced**: Diamond → Archer → One-arm push-ups\n\n💡 **Pro Tips**:\n• Use backpack with books for added resistance\n• Slow tempo (3 seconds down, 1 second up)\n• Focus on squeezing chest at the top\n\n🔥 **Finisher**: Push-up to failure + 10 wall push-ups\n\nNeed other muscle groups for home? 💪"
                }
            }
        elif any(muscle in recent_context for muscle in ["back", "lat"]):
            return {
                "response": {
                    "role": "assistant",
                    "content": "🏠 **HOME BACK WORKOUT** - Creative solutions!\n\n💪 **No Equipment Back Exercises**:\n• **Reverse Snow Angels**: 3 sets x 15 reps (lying face down)\n• **Superman**: 3 sets x 12-15 reps (lower back focus)\n• **Towel Rows**: 3 sets x 10-12 reps (towel around sturdy post)\n• **Prone Y-T-W**: 3 sets x 8 each (rear delt focus)\n\n🪑 **Using Furniture**:\n• **Under-table Rows**: 3 sets x 8-12 reps (lying under table)\n• **Single-arm Rows**: Use heavy bag/luggage as weight\n\n💡 **Creative Equipment**:\n• **Resistance Band**: Best home back investment ($10-15)\n• **Water Jugs**: 1-gallon jugs for rowing motions\n• **Backpack**: Fill with books for weighted rows\n\n🎯 **Focus**: Squeeze shoulder blades together on every rep!\n\nReady to build that V-taper at home? 💪"
                }
            }
        elif any(muscle in recent_context for muscle in ["leg", "squat", "quad"]):
            return {
                "response": {
                    "role": "assistant",
                    "content": "🏠 **HOME LEG WORKOUT** - Bodyweight power!\n\n🦵 **Bodyweight Leg Burners**:\n• **Squats**: 4 sets x 15-20 reps (go deep!)\n• **Jump Squats**: 3 sets x 10 reps (explosive power)\n• **Lunges**: 3 sets x 12 each leg (forward & reverse)\n• **Single-Leg Squats**: 2 sets x 5-8 each leg (pistol progression)\n\n🔥 **Glute Focus**:\n• **Glute Bridges**: 3 sets x 15-20 reps\n• **Single-Leg Bridges**: 3 sets x 10 each leg\n• **Wall Sits**: 3 sets x 30-60 seconds\n\n🏠 **Using Stairs/Steps**:\n• **Step-ups**: 3 sets x 12 each leg\n• **Calf Raises**: 4 sets x 15-20 reps\n• **Bulgarian Split Squats**: 3 sets x 10 each leg\n\n💡 **Intensity Boosters**:\n• Add backpack with books for weight\n• Slow tempo (3 seconds down)\n• Hold bottom position for 2 seconds\n\nReady to feel the burn? 🔥"
                }
            }
        
        # General home workout if no specific muscle context
        return fitness_responses.get("home", "🏠 **HOME FITNESS** - Let's get creative with bodyweight training! What muscle group interests you?")
    
    # Fitness level responses (contextual)
    if any(word in user_lower for word in ["average", "intermediate", "medium"]) and has_context:
        return {
            "response": {
                "role": "assistant", 
                "content": "Perfect! For an **average/intermediate** fitness level, here's your personalized plan:\n\n🏋️ **Strength Training** (3-4x per week):\n• Compound movements: Squats, deadlifts, bench press, rows\n• 3-4 sets of 8-12 reps\n• Progressive overload each week\n\n🏃 **Cardio** (3x per week):\n• 25-35 minutes moderate intensity\n• Mix of running, cycling, or rowing\n• Include 1 HIIT session per week\n\n🧘 **Recovery**:\n• 2 rest days per week\n• 15-20 minutes stretching daily\n• 7-8 hours sleep\n\n📊 **Nutrition Goals**:\n• Protein: 1.6-2.2g per kg body weight\n• Stay hydrated: 2-3L water daily\n\nWould you like me to detail any specific area? 💪"
            }
        }
    
    if any(word in user_lower for word in ["beginner", "new", "start", "first"]) and has_context:
        return {
            "response": {
                "role": "assistant",
                "content": "Excellent! For a **beginner** level, let's start with a solid foundation:\n\n🌟 **Week 1-4 Program**:\n\n🏋️ **Strength** (2-3x per week):\n• Bodyweight squats: 2 sets of 8-12\n• Push-ups (modified if needed): 2 sets of 5-10\n• Planks: 2 sets of 15-30 seconds\n• Walking lunges: 2 sets of 6-8 each leg\n\n🚶 **Cardio** (2-3x per week):\n• 15-20 minutes brisk walking\n• Gradually increase by 2-3 minutes weekly\n\n💡 **Key Tips**:\n• Focus on proper form over intensity\n• Rest 1-2 days between workouts\n• Listen to your body\n• Stay consistent!\n\n🎯 **Goal**: Build the habit and basic strength foundation\n\nReady to start your fitness journey? Any specific concerns? 🚀"
            }
        }
    
    if any(word in user_lower for word in ["advanced", "expert", "experienced"]) and has_context:
        return {
            "response": {
                "role": "assistant",
                "content": "Great! For an **advanced** fitness level, let's optimize your training:\n\n🔥 **Advanced Program Structure**:\n\n🏋️ **Strength** (4-6x per week):\n• Push/Pull/Legs split or Upper/Lower\n• 4-6 sets of 6-12 reps depending on goals\n• Include periodization (strength, hypertrophy, power phases)\n• Advanced techniques: Drop sets, supersets, tempo work\n\n⚡ **Cardio**:\n• HIIT: 2-3x per week (8-15 minutes)\n• LISS: 1-2x per week (20-40 minutes)\n• Sport-specific conditioning if applicable\n\n📈 **Advanced Strategies**:\n• Deload weeks every 4-6 weeks\n• Track volume, intensity, and recovery metrics\n• Consider specialized programs (powerlifting, bodybuilding, etc.)\n• Advanced nutrition timing and supplementation\n\n🎯 **Focus Areas**:\n• Weak point training\n• Movement quality refinement\n• Performance optimization\n\nWhat's your primary goal? Strength, size, or athletic performance? 💪"
            }
        }
    
    # Enhanced fitness responses with muscle groups and specific workouts
    fitness_responses = {
        "hi": "Hello! I'm REVLINE, your AI fitness assistant! 💪 How can I help you with your fitness journey today?",
        "hello": "Hey there! Ready to crush your fitness goals? I'm here to help with workouts, nutrition, and wellness advice! 🚀",
        "hey": "Hey! Welcome to REVLINE! Let's talk about fitness, nutrition, and wellness. What's your goal? 🎯",
        "help": "I'm here to help you with:\n\n💪 **Workout Plans & Exercise**\n🥗 **Nutrition & Diet Advice**\n🧘 **Wellness & Recovery**\n🏃 **Cardio & Endurance Training**\n🏋️ **Strength & Muscle Building**\n📊 **Fitness Goal Planning**\n\nWhat would you like to know?",
        "workout": "Great question! For an effective workout, I recommend:\n\n🏋️ **Strength Training**: 3-4 sets of compound exercises (squats, deadlifts, bench press)\n⏱️ **Cardio**: 20-30 minutes of moderate intensity\n🧘 **Flexibility**: 10-15 minutes of stretching\n💪 **Progressive Overload**: Gradually increase weight/reps\n\nWhat's your current fitness level? I can create a personalized plan for you!",
        "chest": "🔥 **CHEST WORKOUT** for intermediate level:\n\n🏋️ **Primary Exercises**:\n• **Bench Press**: 4 sets x 8-10 reps (compound movement)\n• **Incline Dumbbell Press**: 3 sets x 10-12 reps (upper chest)\n• **Dips**: 3 sets x 8-15 reps (lower chest focus)\n• **Push-ups**: 2 sets to failure (bodyweight finisher)\n\n💡 **Pro Tips**:\n• Focus on controlled movement and full range of motion\n• Rest 2-3 minutes between heavy sets\n• Progressive overload: add 2.5-5lbs weekly\n• Train chest 2x per week with 48-72h rest\n\n🎯 **Muscle Targets**: Pectoralis major, anterior deltoids, triceps\n\nNeed variations for home or advanced training?",
        "back": "💪 **BACK WORKOUT** for pulling power:\n\n🏋️ **Primary Exercises**:\n• **Deadlifts**: 4 sets x 6-8 reps (full back development)\n• **Pull-ups/Lat Pulldowns**: 3 sets x 8-12 reps (lats)\n• **Barbell Rows**: 3 sets x 8-10 reps (mid-back)\n• **Face Pulls**: 3 sets x 12-15 reps (rear delts & rhomboids)\n\n🎯 **Focus Areas**: Lats, rhomboids, traps, rear delts, erector spinae\n\nWant specific variations or home alternatives?",
        "legs": "🦵 **LEG DAY** - Build serious lower body strength:\n\n🏋️ **Primary Exercises**:\n• **Squats**: 4 sets x 8-10 reps (king of all exercises)\n• **Romanian Deadlifts**: 3 sets x 10-12 reps (hamstrings/glutes)\n• **Lunges**: 3 sets x 12 reps each leg (unilateral strength)\n• **Calf Raises**: 4 sets x 15-20 reps (calves)\n\n🔥 **Advanced Add-ons**:\n• Bulgarian split squats: 2 sets x 10 each leg\n• Wall sits: 3 sets x 30-60 seconds\n\n🎯 **Targets**: Quads, hamstrings, glutes, calves\n\nReady to feel the burn? 💪",
        "shoulders": "💪 **SHOULDER WORKOUT** for 3D delts:\n\n🏋️ **Primary Exercises**:\n• **Overhead Press**: 4 sets x 6-8 reps (compound strength)\n• **Lateral Raises**: 3 sets x 12-15 reps (side delts)\n• **Rear Delt Flyes**: 3 sets x 12-15 reps (rear delts)\n• **Front Raises**: 2 sets x 10-12 reps (front delts)\n\n⚠️ **Safety First**: Shoulders are injury-prone - focus on form!\n• Warm up thoroughly\n• Control the weight\n• Full range of motion\n\n🎯 **Targets**: All three deltoid heads for balanced development",
        "arms": "💪 **ARM WORKOUT** - Biceps & Triceps:\n\n🏋️ **Biceps**:\n• **Barbell Curls**: 3 sets x 8-10 reps\n• **Hammer Curls**: 3 sets x 10-12 reps\n• **Chin-ups**: 2 sets x max reps\n\n🏋️ **Triceps**:\n• **Close-Grip Bench Press**: 3 sets x 8-10 reps\n• **Tricep Dips**: 3 sets x 10-15 reps\n• **Overhead Tricep Extension**: 3 sets x 10-12 reps\n\n💡 **Tip**: Triceps are 2/3 of your arm mass - don't neglect them!\n\nNeed a superset routine?",
        "abs": "🔥 **CORE WORKOUT** for a strong midsection:\n\n💪 **Essential Exercises**:\n• **Planks**: 3 sets x 30-60 seconds (core stability)\n• **Bicycle Crunches**: 3 sets x 20 each side (obliques)\n• **Dead Bugs**: 3 sets x 10 each side (deep core)\n• **Mountain Climbers**: 3 sets x 20 total (cardio + core)\n\n🎯 **Advanced**:\n• Russian twists: 3 sets x 30 seconds\n• Leg raises: 3 sets x 12-15 reps\n\n💡 **Remember**: Abs are made in the kitchen! Diet is crucial for definition.",
        "nutrition": "Excellent! Here's my top nutrition advice:\n\n🥗 **Eat whole foods**: Focus on lean proteins, complex carbs, and healthy fats\n💧 **Stay hydrated**: Aim for 8-10 glasses of water daily\n⏰ **Meal timing**: Eat every 3-4 hours to maintain energy\n📊 **Track macros**: Balance your protein, carbs, and fats\n🍎 **Fruits & Veggies**: 5-7 servings per day\n\nWhat are your specific nutrition goals?",
        "diet": "Here's a solid diet framework:\n\n🥩 **Protein**: 0.8-1g per lb of body weight\n🍚 **Carbs**: 2-3g per lb for active individuals\n🥑 **Fats**: 0.3-0.4g per lb of body weight\n🥬 **Fiber**: 25-35g daily from vegetables and fruits\n⚖️ **Calorie Balance**: Deficit for fat loss, surplus for muscle gain\n\nNeed help calculating your specific macros?",
        "muscle": "Building muscle requires:\n\n🏋️ **Resistance Training**: 3-4x per week\n🥩 **Adequate Protein**: 1.6-2.2g per kg body weight\n😴 **Quality Sleep**: 7-9 hours nightly\n📈 **Progressive Overload**: Gradually increase intensity\n⏰ **Consistency**: Results take 8-12 weeks\n💧 **Hydration**: Essential for muscle function\n\nWhat muscle groups are you focusing on?",
        "10 min": "⚡ **10-MINUTE POWER WORKOUT**:\n\n🔥 **Circuit Training** (45s work, 15s rest):\n\n**Round 1** (3 minutes):\n• Jumping Jacks (45s)\n• Push-ups (45s) \n• Squats (45s)\n\n**Round 2** (3 minutes):\n• Burpees (45s)\n• Plank (45s)\n• Lunges (45s)\n\n**Round 3** (3 minutes):\n• High Knees (45s)\n• Mountain Climbers (45s)\n• Wall Sit (45s)\n\n**Cool Down** (1 minute):\n• Deep breathing & light stretching\n\n💪 **Benefits**: Full-body, high-intensity, no equipment needed!\n🔥 **Calories Burned**: ~80-120 calories",
        "10": "⚡ **10-MINUTE QUICK WORKOUT**:\n\n🏃 **HIIT Circuit** (30s on, 10s rest):\n1. **Jumping Jacks** - Warm up\n2. **Squats** - Lower body power\n3. **Push-ups** - Upper body strength\n4. **Plank** - Core stability\n5. **Burpees** - Full body cardio\n6. **Lunges** - Leg strength\n7. **Mountain Climbers** - Cardio blast\n8. **Wall Sit** - Leg endurance\n\n**Repeat 2 rounds** = 10 minutes total!\n\n💡 **Perfect for**: Busy schedules, home workouts, energy boost\n🔥 **Result**: Increased heart rate, muscle activation, endorphin rush!",
        "home": "🏠 **HOME WORKOUT ESSENTIALS** - No gym needed!\n\n💪 **Upper Body (No Equipment)**:\n• Push-ups (all variations)\n• Pike push-ups (shoulders)\n• Tricep dips (chair/couch)\n• Wall handstand push-ups\n\n🦵 **Lower Body**:\n• Squats & squat jumps\n• Lunges (forward, reverse, lateral)\n• Single-leg glute bridges\n• Calf raises on stairs\n\n🔥 **Full Body HIIT**:\n• Burpees, mountain climbers\n• High knees, jumping jacks\n• Bear crawls, plank variations\n\n📱 **Minimal Equipment Ideas**:\n• Water bottles = dumbbells\n• Backpack = weighted vest\n• Towel = resistance band\n\nWhich muscle group for home training?",
        "variations": "🔄 **EXERCISE VARIATIONS** for different needs:\n\n💪 **Push-up Variations**:\n• **Beginner**: Wall push-ups, knee push-ups\n• **Standard**: Regular push-ups\n• **Advanced**: Diamond, decline, one-arm\n\n🦵 **Squat Variations**:\n• **Beginner**: Chair squats, assisted\n• **Standard**: Bodyweight squats\n• **Advanced**: Jump squats, pistol squats\n\n🏋️ **Equipment Alternatives**:\n• **No weights**: Use water bottles, books\n• **No bench**: Use chair, couch, floor\n• **No pull-up bar**: Resistance bands, towel rows\n\n🎯 **Intensity Modifications**:\n• **Easier**: Longer rest, fewer reps\n• **Harder**: Shorter rest, more reps, add weight\n\nWhat specific exercise needs variation?",
        "equipment": "🏋️ **EQUIPMENT GUIDE** for effective workouts:\n\n🏠 **Home Gym Essentials** (Budget-Friendly):\n• **Resistance Bands**: $10-20 (full body training)\n• **Adjustable Dumbbells**: $50-100 (strength training)\n• **Yoga Mat**: $15-30 (floor exercises, stretching)\n• **Pull-up Bar**: $20-40 (upper body pulling)\n\n💪 **No Equipment? No Problem!**:\n• **Bodyweight**: Push-ups, squats, lunges\n• **Household Items**: Water bottles, backpack, stairs\n• **Furniture**: Chair dips, couch step-ups\n\n🎯 **Progressive Investment**:\n1. **Start**: Resistance bands + mat\n2. **Upgrade**: Add dumbbells\n3. **Advanced**: Pull-up bar + kettlebell\n\nWhat's your equipment situation?"
    }
    
    # Check for specific keywords in user message
    response_content = "That's a great fitness question! I'm here to help with:\n\n💪 **Workouts & Exercise**\n🥗 **Nutrition & Diet**\n🧘 **Wellness & Recovery**\n🏃 **Cardio & Endurance**\n🏋️ **Strength Training**\n📊 **Goal Setting & Tracking**\n\nCould you be more specific about what you'd like to know?"
    
    for keyword, response in fitness_responses.items():
        if keyword in user_lower:
            response_content = response
            break
    
    return {
        "response": {
            "role": "assistant",
            "content": response_content
        }
    }

@app.post("/chat-rag")
async def chat_rag(request: RAGRequest):
    """RAG chat with fitness topic validation and context awareness"""
    
    # Enhanced fitness-related keywords for validation
    fitness_keywords = [
        "workout", "exercise", "fitness", "gym", "training", "muscle", "strength", "cardio", 
        "running", "jogging", "swimming", "cycling", "yoga", "pilates", "weightlifting",
        "nutrition", "diet", "protein", "carbs", "calories", "weight", "fat", "lean",
        "health", "wellness", "recovery", "rest", "sleep", "stretching", "flexibility",
        "bodybuilding", "crossfit", "hiit", "endurance", "sports", "athletic", "physique",
        "supplements", "vitamins", "hydration", "water", "meal", "food", "eating",
        "bulk", "cut", "shred", "tone", "abs", "biceps", "triceps", "legs", "chest",
        "back", "shoulders", "core", "squat", "deadlift", "benchpress", "pushup",
        "pullup", "plank", "burpee", "lunge", "crunch", "situp", "dumbbell", "barbell",
        "hi", "hello", "hey", "revline", "help", "advice", "assistant", "plan",
        # Muscle groups and body parts
        "pecs", "pectorals", "delts", "deltoids", "lats", "latissimus", "traps", "trapezius",
        "rhomboids", "erector", "spine", "glutes", "gluteus", "hamstrings", "quadriceps",
        "quads", "calves", "gastrocnemius", "soleus", "forearms", "bicep", "tricep",
        # Context-aware keywords
        "beginner", "intermediate", "advanced", "average", "level", "experience",
        "start", "starting", "begin", "beginning", "new", "first", "time",
        "more", "less", "increase", "decrease", "better", "improve", "progress",
        "yes", "no", "okay", "sure", "continue", "next", "then", "also", 
        "what about", "how about", "tell me", "show me", "give me", 
        "can you", "will you", "should i",
        # Positive feedback and encouragement
        "thanks", "thank you", "great", "good", "perfect", "awesome",
        "excellent", "amazing", "fantastic", "wonderful", "nice",
        "good job", "well done", "impressive", "helpful", "useful",
        "love it", "like it", "cool", "wow", "nice work", "appreciate",
        "good response", "great response", "well said", "correct", "exactly",
        # Location and equipment
        "home", "house", "apartment", "gym", "equipment", "bodyweight",
        "variations", "alternatives", "options", "modify", "different"
    ]
    
    def is_fitness_related(text):
        """Check if the question is fitness-related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in fitness_keywords)
    
    # Check for positive feedback in document chat context
    user_lower = request.question.lower()
    
    if any(word in user_lower for word in [
        "good job", "great job", "well done", "thanks", "thank you", "great", 
        "good", "perfect", "awesome", "excellent", "amazing", "fantastic", 
        "wonderful", "nice", "helpful", "useful", "love it", "like it", 
        "cool", "wow", "appreciate", "good response", "great response",
        "nice work", "well said", "correct", "right", "exactly"
    ]):
        positive_responses = [
            "Thank you! 💪 I'm REVLINE, your dedicated fitness assistant. Upload fitness documents for expert analysis!",
            "Appreciate the feedback! 🚀 I focus on fitness content only to give you the best health and wellness insights!",
            "Thanks! 🔥 I stay committed to fitness topics - ready to analyze your fitness documents and PDFs!",
            "Glad you understand! 🎯 I'm specialized in fitness to provide expert document analysis. Upload fitness content!",
            "You got it! 💪 I'm your fitness-focused document analyst. Ready for fitness PDFs, workout plans, or nutrition guides!",
            "Exactly! 🌟 I keep document analysis fitness-focused for the best health insights. What fitness document can I help with?"
        ]
        import random
        return {
            "response": {
                "role": "assistant",
                "content": random.choice(positive_responses)
            }
        }
    
    # Check if the question is fitness-related
    if not is_fitness_related(request.question):
        return {
            "response": {
                "role": "assistant",
                "content": "I'm REVLINE, a specialized fitness assistant. I can only help analyze fitness, exercise, nutrition, and wellness content. Please ask questions related to fitness topics about your uploaded document. 📚💪"
            }
        }
    
    return {
        "response": {
            "role": "assistant",
            "content": f"📚 **Document Analysis**: I would analyze your document for: '{request.question}'\n\nBased on your uploaded fitness document, I would provide detailed insights about:\n\n🎯 **Key Points** related to your question\n💡 **Expert Recommendations** from the document\n📊 **Data & Statistics** if available\n🔍 **Relevant Sections** that address your query\n\nThis is a test response! Your RAG system would provide detailed insights from your uploaded fitness documents here. 🔍✨"
        }
    }

@app.post("/upload-pdf")
async def upload_pdf():
    """Simple upload test response"""
    return {"message": "PDF uploaded successfully! (Test mode)"}

if __name__ == "__main__":
    print("🚀 Starting REVLINE Test Server...")
    print("🌟 Your futuristic fitness chatbot UI is ready!")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")