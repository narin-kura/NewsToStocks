import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "../constants/theme";

// avg_sentiment from the API is roughly 0..1 (positive-only average).
export function SentimentBar({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(1, value));
  const color =
    pct >= 0.5 ? Colors.green : pct >= 0.25 ? Colors.warn : Colors.textMuted;
  return (
    <View style={styles.wrap}>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${pct * 100}%`, backgroundColor: color }]} />
      </View>
      <Text style={[styles.label, { color }]}>{value.toFixed(2)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: "row", alignItems: "center", gap: 8, flex: 1 },
  track: {
    flex: 1,
    height: 6,
    backgroundColor: Colors.border,
    borderRadius: 3,
    overflow: "hidden",
  },
  fill: { height: "100%", borderRadius: 3 },
  label: { fontSize: 12, fontWeight: "700", minWidth: 34, textAlign: "right" },
});
