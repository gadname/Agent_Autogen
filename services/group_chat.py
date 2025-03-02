import os
import time
import tiktoken
from datetime import datetime
from autogen import GroupChat, GroupChatManager
from services.agents import (
    product_manager,
    engineer,
    designer,
    database_analyst,
)


class SoftwareDesignGroupChat:
    """
    ソフトウェア設計のためのグループチャットを管理するクラス
    """

    def __init__(self):
        self.participants = [
            product_manager,
            engineer,
            designer,
            database_analyst,
        ]
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
            )
        self.display_names = {
            "ProductManager": "佐藤（PM）",
            "Engineer": "田中（エンジニア）",
            "Designer": "鈴木（デザイナー）",
            "DatabaseAnalyst": "高橋（データアナリスト）",
        }
        # トークン計測用のエンコーダー
        self.encoder = tiktoken.encoding_for_model("gpt-4o")
        # 統計情報の初期化
        self.stats = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_time": 0,
            "messages": [],
        }

    def create_group_chat(self, max_rounds=25):
        select_speaker_llm_config = {
            "config_list": [
                {
                    "model": "gpt-4o",
                    "api_key": self.openai_api_key,
                }
            ],
            "temperature": 0.9,
        }

        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
            allow_repeat_speaker=True,
            select_speaker_message_template=(
                "以下の会話を読み、次に発言すべき人物を選んでください。\n"
                "議論が活発になるよう、意見の対立がある場合や、前の発言に反論したい人、"
                "または新しい視点を提供できる人を選びましょう。\n"
                "特に、まだ解決していない問題点や、他のメンバーの提案に対して異なる見解を持つ人を優先してください。\n"
                "リストから一つだけ、人物名のみを返してください。"
            ),
            send_introductions=True,
        )

        return GroupChatManager(
            groupchat=group_chat,
            llm_config=select_speaker_llm_config,
        )

    def start_software_design_discussion(self, user_message, max_turns=25):
        """
        ユーザーの要件に基づいて設計議論を開始する
        """
        # 開始時間を記録
        start_time = time.time()

        manager = self.create_group_chat(max_rounds=max_turns)

        initial_message = f"""
# プロジェクト要件

クライアントからの要件: 「{user_message}」

## 議論のガイドライン

この会議では、上記の要件に基づいて最適な設計と実装方法について議論します。
各自の専門性を活かしつつ、他のメンバーの意見に対して率直に意見を述べてください。

特に以下の点について深く議論してください：
1. 技術選定の根拠と代替案（コスト、時間、品質のトレードオフ）
2. ユーザー体験と技術的制約のバランス
3. データ収集・分析戦略とプライバシー配慮
4. スケーラビリティと将来の拡張性
5. 実装の優先順位とフェーズ分け

意見が対立した場合は、それぞれの立場から根拠を示して議論してください。
最終的には具体的なアクションプランと担当者を決定します。

それでは、佐藤さんから議論を始めてください。
"""
        # 初期メッセージのトークン数を計算
        initial_tokens = len(self.encoder.encode(initial_message))
        self.stats["prompt_tokens"] += initial_tokens
        self.stats["total_tokens"] += initial_tokens

        # オリジナルのメッセージ処理関数を保存
        original_process_message = manager._process_received_message

        # メッセージ処理関数をオーバーライド
        def custom_process_message(message, sender, silent):
            message_start_time = time.time()
            result = original_process_message(message, sender, silent)
            message_end_time = time.time()

            # メッセージの統計情報を記録
            if not silent and sender in self.display_names:
                message_tokens = len(self.encoder.encode(message))
                response_time = message_end_time - message_start_time

                self.stats["messages"].append(
                    {
                        "sender": self.display_names.get(sender, sender),
                        "time": response_time,
                        "tokens": message_tokens,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    }
                )

            return result

        # カスタム関数に置き換え
        manager._process_received_message = custom_process_message

        # 会話を開始
        manager.initiate_chat(
            product_manager,
            message=initial_message,
        )

        # 終了時間を記録
        end_time = time.time()
        self.stats["total_time"] = end_time - start_time

        # 会話終了後
        conversation_history = manager.groupchat.messages

        # トークン数をリセット
        self.stats["prompt_tokens"] = len(self.encoder.encode(initial_message))
        self.stats["completion_tokens"] = 0
        self.stats["total_tokens"] = self.stats["prompt_tokens"]

        # 会話履歴から計測
        for msg in conversation_history:
            content = msg.get("content", "")
            if not content or not isinstance(content, str):
                continue

            # 内部メッセージを除外
            if "Next speaker" in content or "(to chat_manager)" in content:
                continue

            tokens = len(self.encoder.encode(content))

            # 役割に基づいてトークンをカウント
            role = msg.get("role", "")
            if role == "user" or role == "system":
                self.stats["prompt_tokens"] += tokens
            elif role == "assistant":
                self.stats["completion_tokens"] += tokens

            # 送信者に基づいてカウント（役割が設定されていない場合）
            elif msg.get("sender") == "chat_manager":
                self.stats["prompt_tokens"] += tokens
            else:
                self.stats["completion_tokens"] += tokens

            # 各メッセージの統計を記録
            if msg.get("sender") in self.display_names:
                self.stats["messages"].append(
                    {
                        "sender": self.display_names.get(
                            msg.get("sender"), msg.get("sender")
                        ),
                        "time": msg.get("time", 0),  # 時間情報がある場合
                        "tokens": tokens,
                        "timestamp": msg.get(
                            "timestamp", datetime.now().strftime("%H:%M:%S")
                        ),
                    }
                )

        self.stats["total_tokens"] = (
            self.stats["prompt_tokens"] + self.stats["completion_tokens"]
        )

        # 会話履歴を整形
        conversation_history = self._format_conversation(conversation_history)

        # 統計情報を追加
        conversation_history += self._format_stats()

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            display_name = self.display_names.get(sender, sender)
            content = msg.get("content", "")

            # 自動選択メッセージや内部メッセージを除外
            if "Next speaker" in content or "(to chat_manager)" in content:
                continue

            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text

    def _format_stats(self):
        """統計情報を整形する"""
        stats_text = "\n\n# 統計情報\n\n"

        # 全体の統計
        stats_text += "## 全体統計\n\n"
        stats_text += f"- 合計トークン数: {self.stats['total_tokens']:,} トークン\n"
        stats_text += (
            f"- プロンプトトークン: {self.stats['prompt_tokens']:,} トークン\n"
        )
        stats_text += f"- 応答トークン: {self.stats['completion_tokens']:,} トークン\n"
        stats_text += f"- 合計時間: {self.stats['total_time']:.2f} 秒\n\n"

        # 各メッセージの統計
        stats_text += "## 各発言の統計\n\n"
        stats_text += "| 発言者 | 時刻 | 応答時間 | トークン数 |\n"
        stats_text += "|--------|------|----------|------------|\n"

        for msg in self.stats["messages"]:
            stats_text += f"| {msg['sender']} | {msg['timestamp']} | {msg['time']:.2f}秒 | {msg['tokens']:,} |\n"

        return stats_text


software_design_group = SoftwareDesignGroupChat()
