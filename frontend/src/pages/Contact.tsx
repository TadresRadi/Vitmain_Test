import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import {
  Mail,
  Phone,
  MapPin,
  Clock,
  Send,
  Check,
  MessageCircle,
  Facebook,
  Instagram,
  Youtube,
} from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Contact() {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: '',
    preferredContact: 'email',
  })
  const [isSubmitted, setIsSubmitted] = useState(false)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const selectedPlan = searchParams.get('plan')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate form submission
    setIsSubmitted(true)
    setTimeout(() => {
      setIsSubmitted(false)
      setFormData({
        name: '',
        email: '',
        company: '',
        message: '',
        preferredContact: 'email',
      })
    }, 3000)
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const handleWhatsAppContact = () => {
    // In a real app, this would open WhatsApp with pre-filled message
    window.open("https://wa.me/201234567890?text=Hi! I'm interested in the Premium Plan", '_blank')
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative z-10 min-h-screen pt-24 pb-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-5xl font-bold text-white mb-6">{t('contact.title')}</h1>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">{t('contact.subtitle')}</p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Contact Form */}
            <motion.div
              className="lg:col-span-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="glass-dark border border-white/20 p-8">
                {isSubmitted ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                  >
                    <div className="w-20 h-20 bg-vitamin-base rounded-full flex items-center justify-center mx-auto mb-6">
                      <Check className="h-10 w-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-4">{t('contact.success')}</h3>
                    <p className="text-white/70 mb-6">
                      Thank you for reaching out. Our team will get back to you within 24 hours.
                    </p>
                    <div className="flex gap-4 justify-center">
                      <Button
                        onClick={() => setIsSubmitted(false)}
                        variant="outline"
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        Send Another Message
                      </Button>
                      <Button
                        onClick={() => navigate('/')}
                        className="bg-vitamin-base hover:bg-vitamin-700 text-white"
                      >
                        Back to Home
                      </Button>
                    </div>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-white/80 text-sm font-medium mb-2">
                          {t('contact.name')} *
                        </label>
                        <Input
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          required
                          placeholder="John Doe"
                          className="bg-white/10 border-white/20 text-white placeholder-white/50"
                        />
                      </div>
                      <div>
                        <label className="block text-white/80 text-sm font-medium mb-2">
                          {t('contact.email')} *
                        </label>
                        <Input
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          required
                          placeholder="john@company.com"
                          className="bg-white/10 border-white/20 text-white placeholder-white/50"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">
                        {t('contact.company')}
                      </label>
                      <Input
                        name="company"
                        value={formData.company}
                        onChange={handleInputChange}
                        placeholder="Acme Corporation"
                        className="bg-white/10 border-white/20 text-white placeholder-white/50"
                      />
                    </div>

                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">
                        {t('contact.preferredContact')} *
                      </label>
                      <select
                        name="preferredContact"
                        value={formData.preferredContact}
                        onChange={handleInputChange}
                        className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-vitamin-base"
                      >
                        <option value="email" className="bg-gray-800">
                          Email
                        </option>
                        <option value="whatsapp" className="bg-gray-800">
                          WhatsApp
                        </option>
                        <option value="phone" className="bg-gray-800">
                          Phone Call
                        </option>
                        <option value="scheduled" className="bg-gray-800">
                          Scheduled Call
                        </option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-white/80 text-sm font-medium mb-2">
                        {t('contact.message')} *
                      </label>
                      <textarea
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        required
                        rows={6}
                        placeholder={
                          selectedPlan === 'premium'
                            ? 'Tell us about your business goals and how we can help you achieve them...'
                            : 'How can we help you create amazing advertising campaigns?'
                        }
                        className="w-full bg-white/10 border border-white/20 text-white placeholder-white/50 rounded-lg px-4 py-3 focus:outline-none focus:border-vitamin-base resize-none"
                      />
                    </div>

                    <Button
                      type="submit"
                      className="w-full bg-vitamin-base hover:bg-vitamin-700 text-white py-4 text-lg"
                    >
                      <Send className="mr-2 h-5 w-5" />
                      {t('contact.send')}
                    </Button>
                  </form>
                )}
              </Card>
            </motion.div>

            {/* Contact Information */}
            <motion.div
              className="space-y-6"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              {/* Quick Contact */}
              <Card className="glass-dark border border-white/20 p-6">
                <h3 className="text-xl font-bold text-white mb-4">{t('contact.quickContact')}</h3>
                <div className="space-y-4">
                  <button
                    onClick={handleWhatsAppContact}
                    className="w-full flex items-center gap-3 text-white/80 hover:text-white transition-colors p-3 rounded-lg hover:bg-white/10"
                  >
                    <MessageCircle className="h-5 w-5 text-green-400" />
                    <div className="text-left">
                      <div className="font-medium text-white">WhatsApp</div>
                      <div className="text-sm">+20 123 456 7890</div>
                    </div>
                  </button>

                  <a
                    href="mailto:support@vitamin.com"
                    className="flex items-center gap-3 text-white/80 hover:text-white transition-colors p-3 rounded-lg hover:bg-white/10"
                  >
                    <Mail className="h-5 w-5 text-vitamin-base" />
                    <div className="text-left">
                      <div className="font-medium text-white">Email</div>
                      <div className="text-sm">support@vitamin.com</div>
                    </div>
                  </a>
                </div>
              </Card>

              {/* Office Information */}
              <Card className="glass-dark border border-white/20 p-6">
                <h3 className="text-xl font-bold text-white mb-4">{t('contact.officeInfo')}</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3 text-white/80">
                    <MapPin className="h-5 w-5 text-vitamin-base" />
                    <div>
                      <div className="font-medium text-white">Cairo, Egypt</div>
                      <div className="text-sm">Business District, Tower A</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-white/80">
                    <Clock className="h-5 w-5 text-vitamin-base" />
                    <div>
                      <div className="font-medium text-white">{t('contact.businessHours')}</div>
                      <div className="text-sm">Mon - Fri: 9:00 AM - 6:00 PM</div>
                      <div className="text-sm">Sat: 10:00 AM - 2:00 PM</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-white/80">
                    <Phone className="h-5 w-5 text-vitamin-base" />
                    <div>
                      <div className="font-medium text-white">{t('contact.phone')}</div>
                      <div className="text-sm">+20 2 1234 5678</div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Social Media */}
              <Card className="glass-dark border border-white/20 p-6 min-h-[220px] flex flex-col justify-center">
                <h3 className="text-xl font-bold text-white mb-4">{t('contact.followUs')}</h3>
                <div className="flex gap-4">
                  <a
                    href="https://facebook.com/vitaminai"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-white/10 border border-white/20 rounded-lg flex items-center justify-center text-white/80 hover:text-[#1877F2] hover:border-[#1877F2] transition-all"
                  >
                    <Facebook className="h-5 w-5" />
                  </a>
                  <a
                    href="https://instagram.com/vitaminai"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-white/10 border border-white/20 rounded-lg flex items-center justify-center text-white/80 hover:text-[#E4405F] hover:border-[#E4405F] transition-all"
                  >
                    <Instagram className="h-5 w-5" />
                  </a>
                  <a
                    href="https://youtube.com/@vitaminai"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-white/10 border border-white/20 rounded-lg flex items-center justify-center text-white/80 hover:text-[#FF0000] hover:border-[#FF0000] transition-all"
                  >
                    <Youtube className="h-5 w-5" />
                  </a>
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
