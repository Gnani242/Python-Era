'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { lessonAPI, executeAPI, progressAPI } from '@/lib/api';
import Link from 'next/link';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

interface Lesson {
  day_number: number;
  topic: string;
  content: string;
  question: string;
  completed: boolean;
  study_time: number;
  practice_time: number;
}

export default function LearnPage() {
  const router = useRouter();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [code, setCode] = useState('# Write your code here\nprint("Hello, Python!")');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [studyTime, setStudyTime] = useState(0);
  const [practiceTime, setPracticeTime] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const studyTimeRef = useRef<number>(0);
  const practiceTimeRef = useRef<number>(0);
  const isPracticeRef = useRef<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    loadLesson();
    startTimer();

    return () => {
      stopTimer();
      saveTime();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  useEffect(() => {
    // Save time every 30 seconds
    const interval = setInterval(() => {
      saveTime();
    }, 30000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadLesson = async () => {
    try {
      const data = await lessonAPI.getTodayLesson();
      setLesson(data);
      setCompleted(data.completed);
      setStudyTime(data.study_time);
      setPracticeTime(data.practice_time);
      studyTimeRef.current = data.study_time;
      practiceTimeRef.current = data.practice_time;
      setCode(data.question ? `# ${data.question}\n\n` : '# Write your code here\nprint("Hello, Python!")');
    } catch (error: any) {
      console.error('Error loading lesson:', error);
      if (error.response?.status === 404) {
        alert('No lesson available for today. Please contact an admin.');
        router.push('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const startTimer = () => {
    isPracticeRef.current = false;
    
    timerRef.current = setInterval(() => {
      if (isPracticeRef.current) {
        practiceTimeRef.current += 1;
        setPracticeTime(practiceTimeRef.current);
      } else {
        studyTimeRef.current += 1;
        setStudyTime(studyTimeRef.current);
      }
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const saveTime = async () => {
    try {
      await progressAPI.updateTime(studyTimeRef.current, practiceTimeRef.current);
    } catch (error) {
      console.error('Error saving time:', error);
    }
  };

  const handleRun = async () => {
    if (!code.trim()) {
      setError('Please write some code first');
      return;
    }

    setExecuting(true);
    setError('');
    setOutput('');
    isPracticeRef.current = true;

    try {
      const result = await executeAPI.executeCode(code);
      if (result.error) {
        setError(result.error);
      } else {
        setOutput(result.output || '(no output)');
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || 'An error occurred while executing code');
    } finally {
      setExecuting(false);
    }
  };

  const handleComplete = async () => {
    try {
      await progressAPI.completeTask();
      setCompleted(true);
      alert('Congratulations! Task completed. Your streak has been updated.');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error completing task');
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    return `${minutes}m ${secs}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No lesson available</p>
          <Link href="/dashboard" className="text-blue-600 hover:underline mt-4 inline-block">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-2xl font-bold text-gray-800">
                Python Era
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Study: {formatTime(studyTime)} | Practice: {formatTime(practiceTime)}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-3xl font-bold text-gray-800">
              Day {lesson.day_number}: {lesson.topic}
            </h1>
            {completed && (
              <span className="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
                ✓ Completed
              </span>
            )}
          </div>

          <div className="prose max-w-none mb-6">
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Learning Content</h3>
              <div className="text-gray-700 whitespace-pre-wrap">{lesson.content}</div>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">Practice Question</h3>
              <div className="text-gray-700 whitespace-pre-wrap">{lesson.question}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">Code Editor</h2>
              <button
                onClick={handleRun}
                disabled={executing}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executing ? 'Running...' : '▶ Run Code'}
              </button>
            </div>
            <div className="border border-gray-300 rounded-lg overflow-hidden" style={{ height: '500px' }}>
              <MonacoEditor
                height="500px"
                defaultLanguage="python"
                value={code}
                onChange={(value) => setCode(value || '')}
                theme="vs-light"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: 'on',
                }}
              />
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Output</h2>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-40 overflow-y-auto">
                {output || <span className="text-gray-500">Run your code to see output here...</span>}
              </div>
            </div>

            {error && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-red-800 mb-4">Error</h2>
                <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg font-mono text-sm h-40 overflow-y-auto whitespace-pre-wrap">
                  {error}
                </div>
              </div>
            )}

            {!completed && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <button
                  onClick={handleComplete}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-lg"
                >
                  ✓ Mark as Complete
                </button>
                <p className="text-sm text-gray-500 mt-2 text-center">
                  Mark this task as complete when you've solved the problem
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

