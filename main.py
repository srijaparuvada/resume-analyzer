from app import app

def main():
    """
    Main entry point for the Resume Analyzer application.
    Starts the Flask development server.
    """
    print("🚀 Starting Resume Analyzer...")
    print("📊 Loading job database and skills...")
    print("🌐 Server will be available at: http://localhost:8080")
    print("✨ Ready to analyze resumes!")
    print("-" * 50)
    
    # Run the Flask application
    app.run(debug=True, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
