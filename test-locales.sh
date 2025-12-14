#!/bin/bash

# Test script to verify all locales are built correctly

echo "==================================="
echo "Multilingual Build Verification"
echo "==================================="
echo ""

echo "✅ Checking build directory structure..."
echo ""

# Check English build
if [ -d "build/docs" ]; then
    echo "✅ English build: FOUND"
    echo "   - build/docs/"
else
    echo "❌ English build: MISSING"
fi

# Check Urdu build
if [ -d "build/ur/docs" ]; then
    echo "✅ Urdu build: FOUND"
    echo "   - build/ur/docs/"
else
    echo "❌ Urdu build: MISSING"
fi

# Check Japanese build
if [ -d "build/ja/docs" ]; then
    echo "✅ Japanese build: FOUND"
    echo "   - build/ja/docs/"
else
    echo "❌ Japanese build: MISSING"
fi

echo ""
echo "==================================="
echo "Next Steps:"
echo "==================================="
echo ""
echo "1. Run: npm run serve"
echo "2. Open: http://localhost:3000/physical-ai-humanoid-textbook/"
echo "3. Test language switcher:"
echo "   - Click 'English' → Should show English"
echo "   - Click 'اردو' → Should show Urdu (RTL)"
echo "   - Click '日本語' → Should show Japanese"
echo ""
echo "All URLs should work without 404 errors!"
echo ""
