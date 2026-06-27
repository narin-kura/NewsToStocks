import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../constants/theme";
import type { Price } from "../constants/api";

export function PriceTag({ price, size = "md" }: { price: Price; size?: "sm" | "md" }) {
  if (!price) {
    return <Text style={styles.na}>No price</Text>;
  }
  const pct = price.change_pct;
  const up = pct != null && pct > 0;
  const down = pct != null && pct < 0;
  const color = up ? Colors.green : down ? Colors.red : Colors.textMuted;
  const big = size === "md";

  return (
    <View style={styles.row}>
      <Text style={[styles.price, big ? styles.priceMd : styles.priceSm]}>
        ${price.price.toFixed(2)}
      </Text>
      {pct != null && (
        <View style={[styles.pill, { backgroundColor: color + "22" }]}>
          <Ionicons
            name={up ? "caret-up" : down ? "caret-down" : "remove"}
            size={big ? 13 : 11}
            color={color}
          />
          <Text style={[styles.pct, { color, fontSize: big ? 13 : 11 }]}>
            {Math.abs(pct).toFixed(2)}%
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", gap: 8 },
  price: { color: Colors.text, fontWeight: "700" },
  priceMd: { fontSize: 16 },
  priceSm: { fontSize: 14 },
  pill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
  },
  pct: { fontWeight: "700" },
  na: { color: Colors.textMuted, fontSize: 12, fontStyle: "italic" },
});
