interface RatingPickerProps {
  value: number
  onChange: (rating: number) => void
}

export function RatingPicker({ value, onChange }: RatingPickerProps) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
        <button
          key={rating}
          onClick={() => onChange(rating)}
          className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
            value === rating
              ? 'bg-vitamin-base text-white'
              : 'bg-white/10 text-white/60 hover:bg-white/20'
          }`}
        >
          {rating}
        </button>
      ))}
    </div>
  )
}