import React from "react";
import { Text, StyleSheet, TouchableOpacity, View, Linking } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../constants/theme";
import type { Article } from "../constants/api";

export function ArticleItem({ article, tone = "pos" }: { article: Article; tone?: "pos" | "neg" }) {
  const accent = tone === "pos" ? Colors.green : Colors.red;
  const open = () => {
    if (article.url) Linking.openURL(article.url).catch(() => {});
  };
  return (
    <TouchableOpacity style={styles.row} onPress={open} activeOpacity={0.7}>
      <View style={[styles.dot, { backgroundColor: accent }]} />
      <View style={{ flex: 1 }}>
        <Text style={styles.preview} numberOfLines={3}>
          {article.preview}
        </Text>
        <View style={styles.metaRow}>
          {!!article.source && <Text style={styles.source}>{article.source}</Text>}
          <Ionicons name="open-outline" size={12} color={Colors.textMuted} />
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: 10,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  dot: { width: 7, height: 7, borderRadius: 4, marginTop: 6 },
  preview: { color: Colors.text, fontSize: 13, lineHeight: 19 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: 5 },
  source: { color: Colors.textMuted, fontSize: 11, fontWeight: "600" },
});
