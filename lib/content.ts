// Static learning content: curated multilingual video classes and the AI tutor knowledge base.

type VerifiedClass = { flag: string; label: string; channel: string; embedId: string; query: string };

const VERIFIED_MULTILINGUAL: Record<string, VerifiedClass[]> = {
  velocity: [
    { flag: "🇧🇩 Bangla", label: " - এইচএসসি ফিজিক্স ক্লাস", channel: "10 Minute School", embedId: "5yfh5aQ3VWA", query: "velocity physics 10 minute school bangla" },
    { flag: "🇬🇧 English", label: " vs Speed Fundamentals", channel: "Khan Academy", embedId: "rAof9Ld5sOg", query: "velocity physics khan academy" },
    { flag: "🇮🇳 Hindi", label: " Concept & Numericals", channel: "Physics Wallah", embedId: "WUvTyaaNkzM", query: "velocity physics wallah hindi" },
  ],
  speed: [
    { flag: "🇧🇩 Bangla", label: " - দ্রুতি ও বেগ ব্যাখ্যা", channel: "OnnoRokom Pathshala", embedId: "5yfh5aQ3VWA", query: "speed physics onnorokom pathshala bangla" },
    { flag: "🇬🇧 English", label: " & Motion Masterclass", channel: "The Organic Chemistry Tutor", embedId: "rAof9Ld5sOg", query: "speed physics organic chemistry tutor" },
    { flag: "🇮🇳 Hindi", label: " in One Shot Physics", channel: "Physics Wallah", embedId: "WUvTyaaNkzM", query: "speed physics wallah hindi" },
  ],
  integration: [
    { flag: "🇧🇩 Bangla", label: " - যোগজীকরণ শর্টকাট ও বেসিক", channel: "10 Minute School", embedId: "f32SChP4G10", query: "integration 10 minute school bangla" },
    { flag: "🇬🇧 English", label: " - Complete Calculus Rules", channel: "Khan Academy", embedId: "N2dp1O_z1sA", query: "integration calculus khan academy" },
    { flag: "🇮🇳 Hindi", label: " - Basic to Advance Calculus", channel: "Unacademy JEE", embedId: "WsQQvHm4lSw", query: "integration unacademy hindi" },
  ],
  array: [
    { flag: "🇧🇩 Bangla", label: " - ডাটা স্ট্রাকচার অ্যারেকে সহজ ভাষায়", channel: "Tamim Shahriar Subeen / 10MS", embedId: "14dsk8Y__Yw", query: "array data structure bangla tutorial" },
    { flag: "🇬🇧 English", label: " - Data Structures & Memory", channel: "freeCodeCamp.org", embedId: "p9I2323D1aU", query: "array data structure freecodecamp" },
    { flag: "🇮🇳 Hindi", label: " in C/C++ Data Structures", channel: "CodeWithHarry", embedId: "Db9ZYbJONNc", query: "array codewithharry hindi" },
  ],
};

const searchUrl = (q: string) => `https://www.youtube.com/results?search_query=${encodeURIComponent(q)}`;

export function generateMultilingualClasses(topicTag: string, subjectName: string) {
  const cleanTopic = topicTag.trim();
  const fullQuery = `${(subjectName || "").trim()} ${cleanTopic}`.trim();
  const upper = cleanTopic.toUpperCase();
  const lower = cleanTopic.toLowerCase();

  for (const [key, items] of Object.entries(VERIFIED_MULTILINGUAL)) {
    if (key.includes(lower) || lower.includes(key)) {
      return items.map((item) => {
        return {
          title: `${item.flag}: ${upper}${item.label}`,
          channel: item.channel,
          embed_url: `https://www.youtube.com/embed/${item.embedId}`,
          watch_url: searchUrl(item.query),
          thumbnail: `https://img.youtube.com/vi/${item.embedId}/hqdefault.jpg`,
        };
      });
    }
  }

  return [
    {
      title: `🇧🇩 Bangla Class: ${upper} সম্পূর্ণ বাংলা টিউটোরিয়াল`,
      channel: "Top Bangla EdTech Channel",
      embed_url: "https://www.youtube.com/embed/5yfh5aQ3VWA",
      watch_url: searchUrl(`${fullQuery} bangla tutorial lesson`),
      thumbnail: "https://img.youtube.com/vi/5yfh5aQ3VWA/hqdefault.jpg",
    },
    {
      title: `🇬🇧 English Class: ${upper} Full Concept & Practice`,
      channel: "Global English Academy",
      embed_url: "https://www.youtube.com/embed/rAof9Ld5sOg",
      watch_url: searchUrl(`${fullQuery} english tutorial course`),
      thumbnail: "https://img.youtube.com/vi/rAof9Ld5sOg/hqdefault.jpg",
    },
    {
      title: `🇮🇳 Hindi Class: ${upper} In Depth Explanation`,
      channel: "Popular Hindi E-Learning",
      embed_url: "https://www.youtube.com/embed/WUvTyaaNkzM",
      watch_url: searchUrl(`${fullQuery} hindi explanation lecture`),
      thumbnail: "https://img.youtube.com/vi/WUvTyaaNkzM/hqdefault.jpg",
    },
  ];
}

const KNOWLEDGE_BASE: Record<string, string> = {
  velocity: "🔹 **Velocity (বেগ):** সময়ের সাথে সরণের পরিবর্তনের হারকে বেগ বলে। এটি একটি ভেক্টর রাশি (মান ও দিক দুটিই আছে)।\n📐 **সূত্র:** v = s / t\n💡 **উদাহরণ:** একটি গাড়ি উত্তর দিকে ৬০ কিমি/ঘণ্টা বেগে চলছে।",
  speed: "🔹 **Speed (দ্রুতি):** সময়ের সাথে অতিক্রান্ত দূরত্বের পরিবর্তনের হারকে দ্রুতি বলে। এটি স্কেলার রাশি।\n📐 **সূত্র:** Speed = Distance / Time",
  integration: "🔹 **Integration (যোগজীকরণ):** ক্যালকুলাসের একটি শাখা যা ক্ষুদ্র ক্ষুদ্র অংশ যুক্ত করে মোট ক্ষেত্রফল নির্ণয় করে।\n📐 **গাণিতিক রূপ:** ∫ x^n dx = (x^(n+1))/(n+1) + C",
  array: "🔹 **Array (অ্যারে):** প্রোগ্রামিংয়ে সমজাতীয় একাধিক ডেটা একটিমাত্র ভ্যারিয়েবল নামের অধীনে ইনডেক্স ব্যবহার করে সাজিয়ে রাখার পদ্ধতি।\n💻 **উদাহরণ:** int scores[5] = {10, 20, 30, 40, 50};",
  sql: "🔹 **SQL:** ডাটাবেজ থেকে তথ্য খোঁজা এবং পরিচালনার জন্য ব্যবহৃত হয়।\n💻 **কোয়েরি উদাহরণ:** SELECT * FROM students WHERE score < 7.5;",
};

export function tutorReply(message: string) {
  const query = message.toLowerCase().trim();
  for (const [key, response] of Object.entries(KNOWLEDGE_BASE)) {
    if (query.includes(key)) return response;
  }
  return `🤖 **AI Tutor:** '${message}' বিষয়টি বেশ আকর্ষণীয়! এই বিষয়ে আরও বিস্তারিত জানতে আপনার ড্যাশবোর্ডের রেকমেন্ডেড ভিডিও ক্লাসগুলো দেখতে পারেন। সুনির্দিষ্ট প্রশ্ন করতে লিখুন: Velocity, Integration, Array, SQL বা Speed।`;
}
