import React, { useState, useEffect, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { translate } from '@docusaurus/Translate';
import styles from './styles.module.css';

// Type definitions for Web Speech API
interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

interface VoiceInputProps {
  onTranscript: (text: string, language: string) => void;
  currentLanguage: 'en' | 'ur' | 'ja';
}

const LANGUAGE_CODES = {
  en: 'en-US',
  ur: 'ur-PK',
  ja: 'ja-JP',
} as const;

const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, currentLanguage }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognitionAPI) {
      setIsSupported(true);
      const recognitionInstance = new SpeechRecognitionAPI();
      setRecognition(recognitionInstance);
    } else {
      setIsSupported(false);
    }
  }, []);

  // Initialize Speech Recognition settings
  useEffect(() => {
    if (!recognition) return;

    // Set language based on current UI language
    recognition.lang = LANGUAGE_CODES[currentLanguage];
    recognition.continuous = false; // Stop after one phrase for better UX
    recognition.interimResults = false; // Only final results
    recognition.maxAlternatives = 3; // Get top 3 alternatives for noise filtering

    // Handle recognition results
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const results = event.results;
      const finalResult = results[event.resultIndex];

      if (finalResult.isFinal) {
        // Noise filtering: choose highest confidence alternative
        let bestTranscript = '';
        let bestConfidence = 0;

        for (let i = 0; i < finalResult.length; i++) {
          const alternative = finalResult[i];
          if (alternative.confidence > bestConfidence) {
            bestConfidence = alternative.confidence;
            bestTranscript = alternative.transcript;
          }
        }

        // Detect dominant language from transcript
        const detectedLanguage = detectDominantLanguage(bestTranscript, currentLanguage);

        // Pass transcript to parent component
        onTranscript(bestTranscript, detectedLanguage);
        setIsListening(false);
        setError(null);
      }
    };

    // Handle errors
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);

      const errorMessages = {
        'no-speech': translate({
          id: 'voiceInput.error.noSpeech',
          message: 'No speech detected. Please try again.',
        }),
        'audio-capture': translate({
          id: 'voiceInput.error.audioCapture',
          message: 'Microphone not available.',
        }),
        'not-allowed': translate({
          id: 'voiceInput.error.notAllowed',
          message: 'Microphone access denied. Please grant permission.',
        }),
        'network': translate({
          id: 'voiceInput.error.network',
          message: 'Network error. Please check your connection.',
        }),
      };

      setError(errorMessages[event.error] || translate({
        id: 'voiceInput.error.unknown',
        message: 'Speech recognition error. Please try again.',
      }));
      setIsListening(false);
    };

    // Handle recognition end
    recognition.onend = () => {
      setIsListening(false);
    };
  }, [recognition, currentLanguage, onTranscript]);

  // Detect dominant language using character ranges
  const detectDominantLanguage = (text: string, fallbackLanguage: string): string => {
    const arabicRegex = /[\u0600-\u06FF]/g; // Urdu uses Arabic script
    const japaneseRegex = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/g;
    const englishRegex = /[a-zA-Z]/g;

    const arabicMatches = (text.match(arabicRegex) || []).length;
    const japaneseMatches = (text.match(japaneseRegex) || []).length;
    const englishMatches = (text.match(englishRegex) || []).length;

    const total = arabicMatches + japaneseMatches + englishMatches;

    if (total === 0) return fallbackLanguage;

    // Return language with highest character count
    if (arabicMatches > japaneseMatches && arabicMatches > englishMatches) {
      return 'ur';
    } else if (japaneseMatches > arabicMatches && japaneseMatches > englishMatches) {
      return 'ja';
    } else if (englishMatches > 0) {
      return 'en';
    }

    return fallbackLanguage;
  };

  const toggleListening = useCallback(() => {
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
        setError(null);
      } catch (err) {
        console.error('Failed to start recognition:', err);
        setError(translate({
          id: 'voiceInput.error.startFailed',
          message: 'Failed to start voice input. Please try again.',
        }));
      }
    }
  }, [recognition, isListening]);

  if (!isSupported) {
    return null; // Hide component if not supported
  }

  return (
    <div className={styles.voiceInputContainer}>
      <button
        type="button"
        onClick={toggleListening}
        className={`${styles.voiceButton} ${isListening ? styles.listening : ''}`}
        aria-label={translate({
          id: 'voiceInput.button.ariaLabel',
          message: 'Voice input',
        })}
        title={translate({
          id: 'voiceInput.button.title',
          message: 'Click to speak',
        })}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={styles.micIcon}
        >
          <path
            d="M10 1C8.34315 1 7 2.34315 7 4V10C7 11.6569 8.34315 13 10 13C11.6569 13 13 11.6569 13 10V4C13 2.34315 11.6569 1 10 1Z"
            fill="currentColor"
          />
          <path
            d="M5 9C5.55228 9 6 9.44772 6 10C6 12.7614 8.23858 15 11 15C13.7614 15 16 12.7614 16 10C16 9.44772 16.4477 9 17 9C17.5523 9 18 9.44772 18 10C18 13.866 14.866 17 11 17V19H13C13.5523 19 14 19.4477 14 20C14 20.5523 13.5523 21 13 21H7C6.44772 21 6 20.5523 6 20C6 19.4477 6.44772 19 7 19H9V17C5.13401 17 2 13.866 2 10C2 9.44772 2.44772 9 3 9C3.55228 9 4 9.44772 4 10C4 12.7614 6.23858 15 9 15C11.7614 15 14 12.7614 14 10C14 9.44772 14.4477 9 15 9H5Z"
            fill="currentColor"
          />
        </svg>
      </button>
      {error && (
        <div className={styles.errorMessage} role="alert">
          {error}
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
