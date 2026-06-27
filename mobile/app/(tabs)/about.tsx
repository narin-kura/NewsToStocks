import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../../constants/theme";

const STEPS = [
  { icon: "newspaper-outline", title: "Reads the news", text: "Pulls live financial news from multiple sources throughout the day." },
  { icon: "analytics-outline", title: "Scores sentiment", text: "Runs sentiment analysis on each article and links it to the companies mentioned." },
  { icon: "trending-up-outline", title: "Ranks signals", text: "Surfaces the stocks with the strongest positive coverage, by sector." },
];

export default function AboutScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      <View style={styles.logoWrap}>
        <View style={styles.logo}>
          <Ionicons name="pulse" size={34} color="#fff" />
        </View>
        <Text style={styles.title}>MarketSignal</Text>
        <Text style={styles.tagline}>
          Stocks with the strongest positive sentiment from live financial news.
        </Text>
      </View>

      {STEPS.map((s) => (
        <View key={s.title} style={styles.card}>
          <Ionicons name={s.icon as any} size={22} color={Colors.accent} />
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{s.title}</Text>
            <Text style={styles.cardText}>{s.text}</Text>
          </View>
        </View>
      ))}

      <View style={styles.disclaimerBox}>
        <Ionicons name="warning-outline" size={16} color={Colors.warn} />
        <Text style={styles.disclaimerText}>
          MarketSignal is for informational and educational purposes only. Sentiment is
          derived from public news headlines and is not financial advice. Always do your
          own research before investing.
        </Text>
      </View>

      <Text style={styles.version}>Version 1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg },
  logoWrap: { alignItems: "center", marginBottom: 28, marginTop: 8 },
  logo: {
    width: 72,
    height: 72,
    borderRadius: 20,
    backgroundColor: Colors.accent,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 14,
  },
  title: { color: Colors.text, fontSize: 24, fontWeight: "800" },
  tagline: {
    color: Colors.textMuted,
    fontSize: 14,
    textAlign: "center",
    marginTop: 8,
    lineHeight: 20,
    paddingHorizontal: 20,
  },
  card: {
    flexDirection: "row",
    gap: 14,
    backgroundColor: Colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: 16,
    marginBottom: 12,
    alignItems: "flex-start",
  },
  cardTitle: { color: Colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  cardText: { color: Colors.textMuted, fontSize: 13, lineHeight: 19 },
  disclaimerBox: {
    flexDirection: "row",
    gap: 10,
    backgroundColor: "#1a1200",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#3d2e00",
    padding: 14,
    marginTop: 12,
  },
  disclaimerText: { color: "#a08040", fontSize: 12, lineHeight: 18, flex: 1 },
  version: { color: Colors.textMuted, fontSize: 12, textAlign: "center", marginTop: 24 },
});
