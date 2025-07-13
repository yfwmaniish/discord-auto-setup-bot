@echo off
cls
echo ================================================
echo  Discord Auto Setup Bot - GitHub Push
echo  Username: yfwmaniish
echo ================================================
echo.

echo 🚀 STEP 1: Create GitHub Repository
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: discord-auto-setup-bot
echo 3. Description: Advanced Discord server automation bot with modern slash commands
echo 4. Make it Public (or Private)
echo 5. DO NOT initialize with README
echo 6. Click "Create repository"
echo.
echo Press any key after creating the repository...
pause >nul
echo.

echo 🔄 STEP 2: Pushing to GitHub...
echo.
"C:\Program Files\Git\bin\git.exe" push -u origin main
echo.

if %errorlevel% equ 0 (
    echo ✅ SUCCESS! Your bot is now on GitHub!
    echo.
    echo 🌐 Repository URL: https://github.com/yfwmaniish/discord-auto-setup-bot
    echo.
    echo 🎯 Your advanced Discord bot includes:
    echo   - Role management with custom permissions
    echo   - Verification system with DM codes
    echo   - Interactive chatbot conversations
    echo   - Chat history search functionality
    echo   - Translation system (100+ languages)
    echo   - Modern slash command interface
    echo.
    echo 🚀 Ready to deploy!
) else (
    echo ❌ Push failed. Make sure you created the repository first.
    echo If you already created it, you might need to authenticate with GitHub.
)
echo.
pause
