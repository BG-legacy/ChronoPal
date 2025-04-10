import React, { useState } from 'react';

interface QuestionButtonProps {
  className?: string;
}

const petQuestions = [
  "How are you feeling today?",
  "What's your favorite activity?",
  "Do you want to play a game?",
  "What's your favorite food?",
  "How was your day?",
  "Would you like to take a break?",
  "What's on your mind?",
  "Do you need any help?"
];

const QuestionButton: React.FC<QuestionButtonProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [showResponse, setShowResponse] = useState(false);

  const getRandomQuestion = () => {
    const randomIndex = Math.floor(Math.random() * petQuestions.length);
    return petQuestions[randomIndex];
  };

  const handleOpen = () => {
    setCurrentQuestion(getRandomQuestion());
    setResponse('');
    setShowResponse(false);
    setIsOpen(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowResponse(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setShowResponse(false);
  };

  return (
    <>
      <button
        onClick={handleOpen}
        className={`px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors text-green-400 font-mono ${className}`}
      >
        [Pet Question]
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-gray-900 p-6 rounded-lg max-w-md w-full border-2 border-green-400 text-green-400 font-mono">
            <h2 className="text-2xl font-bold mb-4">{'>'} Pet Question:</h2>
            <p className="text-xl mb-4">{currentQuestion}</p>
            
            {!showResponse ? (
              <form onSubmit={handleSubmit}>
                <textarea
                  value={response}
                  onChange={(e) => setResponse(e.target.value)}
                  className="w-full p-2 bg-gray-800 border-2 border-green-400 rounded-lg mb-4 text-green-400 font-mono"
                  rows={4}
                  placeholder="Type your response here..."
                />
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="px-4 py-2 bg-gray-800 text-green-400 rounded-lg hover:bg-gray-700 border-2 border-green-400"
                  >
                    [Close]
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-gray-800 text-green-400 rounded-lg hover:bg-gray-700 border-2 border-green-400"
                  >
                    [Respond]
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="bg-gray-800 p-4 rounded-lg border-2 border-green-400">
                  <p className="text-green-400">{'>'} Your response:</p>
                  <p className="text-green-400 mt-2">{response}</p>
                </div>
                <button
                  onClick={handleClose}
                  className="w-full px-4 py-2 bg-gray-800 text-green-400 rounded-lg hover:bg-gray-700 border-2 border-green-400"
                >
                  [Close]
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default QuestionButton; 