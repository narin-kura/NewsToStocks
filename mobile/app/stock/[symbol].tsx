import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../../constants/theme";
import { useApi } from "../../hooks/useApi";
import { PriceTag } from "../../components/PriceTag";
import { SentimentBar } from "../../components/SentimentBar";
import { ArticleItem } from "../../components/ArticleItem";
import type { SearchResponse, Signal } from "../../constants/api";

export default function StockDetailScreen() {
  const { symbol } = useLocalSearchParams<{ symbol: string }>();
  const navigation = useNavigation();
  const { call, loading } = useApi();
  const [signal, setSignal] = useState<Signal | null>(null);

  useEffect(() => {
    if (!symbol) return;
    navigation.setOptions({ title: symbol });
    call<SearchResponse>(`/api/search?q=${encodeURIComponent(symbol)}`).then((res) => {
      if (res?.result) setSignal(res.result);
    });
  }, [symbol]);

  if (loading && !signal) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.accent} />
      </View>
    );
  }

  if (!signal) {
    return (
      <View style={styles.center}>
        <Ionicons name="alert-circle-outline" size={42} color={Colors.textMuted} />
        <Text style={styles.muted}>No data for {symbol}.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.symbol}>{signal.symbol}</Text>
            {!!signal.company_name && signal.company_name !== signal.symbol && (
              <Text style={styles.company}>{signal.company_name}</Text>
            )}
          </View>
          <PriceTag price={signal.price} />
        </View>

        <View style={styles.sentimentRow}>
          <Text style={styles.sentimentLabel}>Sentiment</Text>
          <SentimentBar value={signal.avg_sentiment} />
        </View>
        <Text style={styles.mentions}>
          Based on {signal.mentions} positive mention{signal.mentions !== 1 ? "s" : ""} in recent news
        </Text>
      </View>

      {/* Positive articles */}
      {signal.articles.length > 0 && (
        <View style={styles.card}>
          <Text style={[styles.cardTitle, { color: Colors.green }]}>
            <Ionicons name="trending-up" size={15} color={Colors.green} /> Positive coverage
          </Text>
          {signal.articles.map((a, i) => (
            <ArticleItem key={`p${i}`} article={a} tone="pos" />
          ))}
        </View>
      )}

      {/* Negative articles */}
      {signal.neg_articles.length > 0 && (
        <View style={styles.card}>
          <Text style={[styles.cardTitle, { color: Colors.red }]}>
            <Ionicons name="trending-down" size={15} color={Colors.red} /> Negative coverage
          </Text>
          {signal.neg_articles.map((a, i) => (
            <ArticleItem key={`n${i}`} article={a} tone="neg" />
          ))}
        </View>
      )}

      {signal.articles.length === 0 && signal.neg_articles.length === 0 && (
        <View style={styles.center}>
          <Text style={styles.muted}>No recent articles found for {signal.symbol}.</Text>
        </View>
      )}

      <Text style={styles.disclaimer}>
        Sentiment is derived from public news headlines and is not financial advice.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: 50, gap: 12 },
  muted: { color: Colors.textMuted, fontSize: 14, textAlign: "center" },
  header: {
    backgroundColor: Colors.surface,
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" },
  symbol: { color: Colors.text, fontSize: 26, fontWeight: "800", letterSpacing: 0.5 },
  company: { color: Colors.textMuted, fontSize: 13, marginTop: 2 },
  sentimentRow: { flexDirection: "row", alignItems: "center", gap: 12, marginTop: 18 },
  sentimentLabel: { color: Colors.textMuted, fontSize: 12, fontWeight: "600" },
  mentions: { color: Colors.textMuted, fontSize: 12, marginTop: 10 },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: Colors.border,
    margin: 16,
    marginBottom: 4,
    padding: 16,
  },
  cardTitle: { fontSize: 14, fontWeight: "700", marginBottom: 4 },
  disclaimer: {
    color: Colors.textMuted,
    fontSize: 11,
    fontStyle: "italic",
    textAlign: "center",
    marginTop: 20,
    marginHorizontal: 24,
    lineHeight: 16,
  },
});
