import { ArrowRight, Zap, Play, Check } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200">
        <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-orange-500 rounded flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">Zapier</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#" className="text-gray-700 hover:text-gray-900">
              Product
            </a>
            <a href="#" className="text-gray-700 hover:text-gray-900">
              Solutions
            </a>
            <a href="#" className="text-gray-700 hover:text-gray-900">
              Resources
            </a>
            <a href="#" className="text-gray-700 hover:text-gray-900">
              Enterprise
            </a>
            <a href="#" className="text-gray-700 hover:text-gray-900">
              Pricing
            </a>
          </div>

          <div className="flex items-center gap-4">
            <a href="/login" className="text-gray-700 hover:text-gray-900">
              Log in
            </a>
            <a
              href="/signup"
              className="px-5 py-2.5 bg-orange-500 text-white rounded hover:bg-orange-600 transition"
            >
              Sign up
            </a>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold mb-6 leading-tight">
            Automate without limits
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Turn chaos into smooth business operations—with AI, automation, and
            integration all working together in Zapier.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button className="px-8 py-4 bg-orange-500 text-white rounded font-semibold hover:bg-orange-600 transition flex items-center gap-2">
              Get started free
              <ArrowRight className="w-5 h-5" />
            </button>
            <button className="px-8 py-4 border-2 border-gray-900 text-gray-900 rounded font-semibold hover:bg-gray-50 transition flex items-center gap-2">
              <Play className="w-5 h-5" />
              See how it works
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-4">
            Free forever for core features
          </p>
        </div>

        {/* App Integration Visual */}
        <div className="mt-16 relative">
          <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
            {[
              "Gmail",
              "Slack",
              "Google Sheets",
              "HubSpot",
              "Trello",
              "Salesforce",
            ].map((app, i) => (
              <div
                key={i}
                className="bg-white border-2 border-gray-200 rounded-lg p-6 text-center hover:border-orange-500 transition"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-pink-500 rounded-lg mx-auto mb-3"></div>
                <p className="font-semibold text-sm">{app}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-16">
            Do more with automation
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "No-code automation",
                desc: "Build workflows with our visual editor—no coding required",
              },
              {
                title: "6,000+ app integrations",
                desc: "Connect the tools you already use in minutes",
              },
              {
                title: "AI-powered",
                desc: "Let AI handle the heavy lifting in your workflows",
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="bg-white rounded-xl p-8 border border-gray-200"
              >
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                  <Check className="w-6 h-6 text-orange-600" />
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Join millions worldwide who automate their work
          </h2>
          <button className="px-8 py-4 bg-orange-500 text-white rounded font-semibold hover:bg-orange-600 transition">
            Get started—it's free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-5 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-orange-500 rounded flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Zapier</span>
              </div>
            </div>
            {["Product", "Solutions", "Resources", "Company"].map(
              (section, i) => (
                <div key={i}>
                  <h4 className="font-semibold mb-3">{section}</h4>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>
                      <a href="#" className="hover:text-gray-900">
                        Link 1
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-gray-900">
                        Link 2
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-gray-900">
                        Link 3
                      </a>
                    </li>
                  </ul>
                </div>
              ),
            )}
          </div>
          <div className="mt-12 pt-8 border-t border-gray-200 text-sm text-gray-600 text-center">
            © 2024 Zapier Inc. All rights reserved. Zapier Clone made by{" "}
            <a
              href="https://github.com/persuasivepost/zapier-clone"
              className="text-orange-500 hover:text-orange-600 font-semibold"
            >
              persuasivepost
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
