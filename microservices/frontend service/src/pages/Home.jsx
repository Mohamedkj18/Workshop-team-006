import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-20 px-6 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-4">Welcome to LazyMail</h1>
        <p className="text-lg md:text-2xl mb-6">Your intelligent email assistant that learns your style and replies for you.</p>
        <div className="flex justify-center space-x-4">
          <Link to="/signup" className="bg-white text-blue-600 px-6 py-3 rounded-xl font-semibold shadow-md hover:bg-gray-100">Sign Up</Link>
          <Link to="/login" className="bg-transparent border border-white px-6 py-3 rounded-xl font-semibold hover:bg-white hover:text-blue-600">Login</Link>
        </div>
      </section>

      {/* About Us Section */}
      <section className="py-16 px-6 md:px-20 bg-gray-50">
        <h2 className="text-3xl font-bold text-center mb-6">About Us</h2>
        <p className="max-w-3xl mx-auto text-center text-lg">
          LazyMail was built to simplify email communication by harnessing the power of AI. Whether you're replying to clients, students, or colleagues, we learn how you write and automate it — saving time while keeping your unique voice.
        </p>
      </section>

      {/* Features Section */}
      <section className="py-16 px-6 md:px-20">
        <h2 className="text-3xl font-bold text-center mb-10">Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-2xl shadow p-6 text-center">
            <h3 className="text-xl font-semibold mb-2">✍️ AI Replies</h3>
            <p>Let the system auto-generate replies that match your tone and intent.</p>
          </div>
          <div className="bg-white rounded-2xl shadow p-6 text-center">
            <h3 className="text-xl font-semibold mb-2">📚 Learns Your Style</h3>
            <p>Upload past emails and let LazyMail adapt to your unique voice.</p>
          </div>
          <div className="bg-white rounded-2xl shadow p-6 text-center">
            <h3 className="text-xl font-semibold mb-2">📂 Smart Drafts</h3>
            <p>Keep track of AI-generated and personal drafts with easy approval workflows.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
