import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../constants/theme";
import { PriceTag } from "./PriceTag";
import { SentimentBar } from "./SentimentBar";
import type { Signal } from "../constants/api";

export function SignalCard({
  signal,
  rank,
  onPress,
}: {
  signal: Signal;
  rank?: number;
  onPress?: () => void;
}) {
  const topArticle = signal.articles?.[0];
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8}>
      <View style={styles.headerRow}>
        <View style={styles.symbolWrap}>
          {rank != null && <Text style={styles.rank}>#{rank}</Text>}
          <Text style={styles.symbol}>{signal.symbol}</Text>
        </View>
        <PriceTag price={signal.price} />
      </View>

      {!!signal.company_name && signal.company_name !== signal.symbol && (
        <Text style={styles.company} numberOfLines={1}>
          {signal.company_name}
        </Text>
      )}

      <View style={styles.metaRow}>
        <View style={styles.mentions}>
          <Ionicons name="newspaper-outline" size={13} color={Colors.textMuted} />
          <Text style={styles.mentionsText}>
            {signal.mentions} mention{signal.mentions !== 1 ? "s" : ""}
          </Text>
        </View>
        <SentimentBar value={signal.avg_sentiment} />
      </View>

      {!!topArticle && (
        <Text style={styles.preview} numberOfLines={2}>
          “{topArticle.preview}”
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  symbolWrap: { flexDirection: "row", alignItems: "center", gap: 8 },
  rank: { color: Colors.accent, fontSize: 13, fontWeight: "800" },
  symbol: { color: Colors.text, fontSize: 19, fontWeight: "800", letterSpacing: 0.5 },
  company: { color: Colors.textMuted, fontSize: 12, marginTop: 2 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 12, marginTop: 12 },
  mentions: { flexDirection: "row", alignItems: "center", gap: 4 },
  mentionsText: { color: Colors.textMuted, fontSize: 12, fontWeight: "600" },
  preview: {
    color: Colors.text,
    opacity: 0.8,
    fontSize: 13,
    lineHeight: 19,
    marginTop: 12,
    fontStyle: "italic",
  },
});
