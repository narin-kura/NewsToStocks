import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Keyboard,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../../constants/theme";
import { useApi } from "../../hooks/useApi";
import { SignalCard } from "../../components/SignalCard";
import type { SearchResponse } from "../../constants/api";

export default function SearchScreen() {
  const router = useRouter();
  const { call, loading } = useApi();
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SearchResponse | null>(null);

  const onSearch = useCallback(async () => {
    const query = q.trim();
    if (!query) return;
    Keyboard.dismiss();
    const res = await call<SearchResponse>(`/api/search?q=${encodeURIComponent(query)}`);
    if (res) setResult(res);
  }, [q, call]);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ paddingBottom: 40 }}
      keyboardShouldPersistTaps="handled"
    >
      <View style={styles.inputRow}>
        <Ionicons name="search" size={18} color={Colors.textMuted} style={{ marginLeft: 12 }} />
        <TextInput
          style={styles.input}
          placeholder="Ticker or company (AAPL, Tesla, NVDA…)"
          placeholderTextColor={Colors.textMuted}
          value={q}
          onChangeText={setQ}
          onSubmitEditing={onSearch}
          autoCapitalize="characters"
          returnKeyType="search"
        />
        <TouchableOpacity style={styles.goBtn} onPress={onSearch} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.goText}>Go</Text>
          )}
        </TouchableOpacity>
      </View>

      {result && !result.found && (
        <View style={styles.empty}>
          <Ionicons name="help-circle-outline" size={42} color={Colors.textMuted} />
          <Text style={styles.emptyTitle}>“{result.query}” not found</Text>
          <Text style={styles.emptyText}>
            Try a stock ticker (e.g. AAPL) or a well-known company name.
          </Text>
        </View>
      )}

      {result?.found && result.result && (
        <>
          <Text style={styles.sectionLabel}>
            Sentiment from {result.result.mentions} recent article
            {result.result.mentions !== 1 ? "s" : ""}
          </Text>
          <SignalCard
            signal={result.result}
            onPress={() =>
              router.push({
                pathname: "/stock/[symbol]",
                params: { symbol: result.result!.symbol },
              })
            }
          />
          {result.result.mentions === 0 && (
            <Text style={styles.note}>
              No strongly positive news right now — tap the card for details.
            </Text>
          )}
        </>
      )}

      {!result && (
        <View style={styles.empty}>
          <Ionicons name="newspaper-outline" size={42} color={Colors.textMuted} />
          <Text style={styles.emptyText}>
            Search any stock to see how today’s financial news feels about it.
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    margin: 16,
  },
  input: {
    flex: 1,
    color: Colors.text,
    fontSize: 15,
    paddingVertical: 12,
    paddingHorizontal: 10,
  },
  goBtn: {
    backgroundColor: Colors.accent,
    borderRadius: 10,
    paddingHorizontal: 18,
    paddingVertical: 10,
    margin: 5,
  },
  goText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  sectionLabel: {
    color: Colors.textMuted,
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginHorizontal: 18,
    marginBottom: 10,
  },
  note: { color: Colors.textMuted, fontSize: 12, marginHorizontal: 18, fontStyle: "italic" },
  empty: { alignItems: "center", padding: 50, gap: 12 },
  emptyTitle: { color: Colors.text, fontSize: 17, fontWeight: "700" },
  emptyText: { color: Colors.textMuted, fontSize: 14, textAlign: "center", lineHeight: 20 },
});
