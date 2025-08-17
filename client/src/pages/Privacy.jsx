export default function Privacy() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="prose prose-lg max-w-none">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Privacy Policy
        </h1>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6 mb-8">
          <p className="text-blue-800 dark:text-blue-200 mb-2">
            <strong>Last Updated:</strong> August 4, 2025
          </p>
          <p className="text-blue-700 dark:text-blue-300">
            This Privacy Policy describes how CapeControl collects, uses, and protects your information.
          </p>
        </div>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Company Information
          </h2>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
            <div className="space-y-2 text-gray-700 dark:text-gray-300">
              <p><strong>Legal Entity:</strong> Cape Craft Projects CC</p>
              <p><strong>VAT Number:</strong> 4270105119</p>
              <p><strong>Trading Name:</strong> Cape Control</p>
              <p><strong>Platform:</strong> CapeControl (formerly LocalStorm)</p>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Information We Collect
          </h2>
          <div className="space-y-4 text-gray-700 dark:text-gray-300">
            <p>
              <strong>Account Information:</strong> When you create an account, we collect your email address, 
              password (encrypted), and profile information you choose to provide.
            </p>
            <p>
              <strong>Usage Data:</strong> We collect information about how you use our platform, including 
              API requests, feature usage, and performance metrics to improve our services.
            </p>
            <p>
              <strong>Payment Information:</strong> Payment data is processed securely through Stripe. 
              We store transaction records but not your payment card details.
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            How We Use Your Information
          </h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
            <li>Provide and maintain our AI platform services</li>
            <li>Process payments and manage subscriptions</li>
            <li>Send important account and service updates</li>
            <li>Improve our platform based on usage analytics</li>
            <li>Ensure security and prevent fraud</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Data Security
          </h2>
          <div className="space-y-4 text-gray-700 dark:text-gray-300">
            <p>
              We implement enterprise-grade security measures including:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>End-to-end encryption for data in transit</li>
              <li>Encrypted storage for sensitive data</li>
              <li>Regular security audits and monitoring</li>
              <li>Access controls and authentication systems</li>
              <li>DDoS protection and input sanitization</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Third-Party Services
          </h2>
          <div className="space-y-4 text-gray-700 dark:text-gray-300">
            <p>
              We work with trusted third-party services:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Stripe:</strong> Payment processing (subject to Stripe's privacy policy)</li>
              <li><strong>Heroku:</strong> Cloud hosting and infrastructure</li>
              <li><strong>AI Providers:</strong> OpenAI, Anthropic, Google (for AI services)</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Your Rights
          </h2>
          <div className="space-y-4 text-gray-700 dark:text-gray-300">
            <p>You have the right to:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Access your personal data</li>
              <li>Correct inaccurate information</li>
              <li>Delete your account and associated data</li>
              <li>Export your data</li>
              <li>Opt out of non-essential communications</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Contact Us
          </h2>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              If you have questions about this Privacy Policy or your data, please contact us:
            </p>
            <div className="space-y-2 text-gray-700 dark:text-gray-300">
              <p><strong>Company:</strong> Cape Craft Projects CC (VAT: 4270105119) trading as Cape Control</p>
              <p><strong>Email:</strong> <a href="mailto:contact@cape-control.com" className="text-blue-600 dark:text-blue-400 hover:underline">contact@cape-control.com</a></p>
              <p><strong>Project:</strong> CapeControl (LocalStorm)</p>
              <p><strong>Repository:</strong> <a href="https://github.com/robert1948/localstorm" className="text-blue-600 dark:text-blue-400 hover:underline">github.com/robert1948/localstorm</a></p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
