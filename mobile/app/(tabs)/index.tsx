import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../../constants/theme";
import { useApi } from "../../hooks/useApi";
import { SignalCard } from "../../components/SignalCard";
import { SectorChips } from "../../components/SectorChips";
import type { SignalsResponse, TabsResponse, Tab, Signal } from "../../constants/api";

const DEFAULT_SORTS: Tab[] = [
  { key: "score", label: "Top Picks" },
  { key: "gainers", label: "▲ Gainers" },
  { key: "losers", label: "▼ Losers" },
  { key: "alpha", label: "A → Z" },
];

export default function SignalsScreen() {
  const router = useRouter();
  const { call } = useApi();

  const [tabs, setTabs] = useState<Tab[]>([{ key: "", label: "All" }]);
  const [sorts, setSorts] = useState<Tab[]>(DEFAULT_SORTS);
  const [sector, setSector] = useState("");
  const [sort, setSort] = useState("score");

  const [data, setData] = useState<SignalsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Load sector tabs + sort options once
  useEffect(() => {
    call<TabsResponse>("/api/tabs").then((res) => {
      if (res) {
        if (res.tabs?.length) setTabs(res.tabs);
        if (res.sorts?.length) setSorts(res.sorts);
      }
    });
  }, []);

  const load = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      const res = await call<SignalsResponse>(
        `/api/signals?sector=${encodeURIComponent(sector)}&sort=${encodeURIComponent(sort)}`
      );
      if (res) setData(res);
      setLoading(false);
      setRefreshing(false);
    },
    [sector, sort, call]
  );

  useEffect(() => {
    load();
  }, [sector, sort]);

  const openDetail = (s: Signal) =>
    router.push({ pathname: "/stock/[symbol]", params: { symbol: s.symbol } });

  const perf = data?.performance;

  return (
    <View style={styles.container}>
      <SectorChips tabs={tabs} active={sector} onChange={setSector} />

      {/* Sort row */}
      <View style={styles.sortRow}>
        {sorts.map((s) => {
          const sel = s.key === sort;
          return (
            <TouchableOpacity key={s.key} onPress={() => setSort(s.key)}>
              <Text style={[styles.sortItem, sel && styles.sortItemActive]}>{s.label}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Performance summary */}
      {perf && (
        <View style={styles.perfRow}>
          <Text style={styles.perfText}>
            <Text style={{ color: Colors.green }}>▲ {perf.up}</Text>
            {"   "}
            <Text style={{ color: Colors.red }}>▼ {perf.down}</Text>
            {"   "}
            <Text style={{ color: Colors.textMuted }}>● {perf.flat}</Text>
          </Text>
          {data && (
            <Text style={styles.cacheText}>
              {data.articles_count} articles · {data.cache_age_min}m ago
            </Text>
          )}
        </View>
      )}

      {loading && !data ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Scanning the news…</Text>
        </View>
      ) : (
        <FlatList
          data={data?.signals ?? []}
          keyExtractor={(item) => item.symbol}
          renderItem={({ item, index }) => (
            <SignalCard signal={item} rank={index + 1} onPress={() => openDetail(item)} />
          )}
          contentContainerStyle={{ paddingVertical: 12 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => load(true)}
              tintColor={Colors.accent}
            />
          }
          ListEmptyComponent={
            <View style={styles.center}>
              <Ionicons name="cloud-offline-outline" size={42} color={Colors.textMuted} />
              <Text style={styles.loadingText}>
                No signals yet — pull to refresh in a moment.
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg, paddingTop: 10 },
  sortRow: {
    flexDirection: "row",
    gap: 18,
    paddingHorizontal: 18,
    paddingVertical: 12,
  },
  sortItem: { color: Colors.textMuted, fontSize: 13, fontWeight: "600" },
  sortItemActive: { color: Colors.text, textDecorationLine: "underline" },
  perfRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 18,
    paddingBottom: 8,
  },
  perfText: { fontSize: 13, fontWeight: "700" },
  cacheText: { color: Colors.textMuted, fontSize: 11 },
  center: { alignItems: "center", justifyContent: "center", padding: 50, gap: 12 },
  loadingText: { color: Colors.textMuted, fontSize: 14, textAlign: "center" },
});
