/** Accessible language picker — <select> with proper <label>. */

import { formatLanguageName } from "../lib/format";

const SUPPORTED_LANGUAGES = [
  "en", "es", "fr", "pt", "ar", "de", "ja", "zh", "ko", "hi", "it", "nl",
] as const;

interface Props {
  value: string;
  onChange: (language: string) => void;
}

export function LanguageSelector({ value, onChange }: Props) {
  return (
    <div className="language-selector">
      <label htmlFor="language-select">Language</label>
      <select
        id="language-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {SUPPORTED_LANGUAGES.map((code) => (
          <option key={code} value={code}>
            {formatLanguageName(code)}
          </option>
        ))}
      </select>
    </div>
  );
}
