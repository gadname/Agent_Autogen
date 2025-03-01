import os
from autogen import GroupChat, GroupChatManager
from services.agents import (
    cognitive_therapist,
    mindfulness_coach,
    solution_focused_therapist,
    patient,
)


class CounselingGroupChat:
    """
    カウンセリングのためのグループチャットを管理するクラス
    """

    def __init__(self):
        self.participants = [
            patient,
            cognitive_therapist,
            mindfulness_coach,
            solution_focused_therapist,
        ]
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
            )
        self.display_names = {
            "CognitiveBehaviorTherapist": "認知行動療法専門家",
            "MindfulnessCoach": "マインドフルネス指導者",
            "SolutionFocusedTherapist": "解決志向型セラピスト",
            "Patient": "患者",
        }

    def create_group_chat(self, max_rounds=10):
        """
        グループチャットを作成する
        """
        select_speaker_llm_config = {
            "config_list": [
                {
                    "model": "gpt-4o-mini",
                    "api_key": self.openai_api_key,
                }
            ]
        }

        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
            select_speaker_message_template=(
                "以下の会話を読み、次に発言すべき専門家を{agentlist}から選んでください。"
                "直前の発言に対して質問や補足、同意/反対の意見を述べるのに最適な専門家を選びましょう。"
                "特に、まだ発言していない専門家や、直前の発言に関連する専門知識を持つ人物を優先してください。"
                "対話を活性化させるために、異なる視点を持つ専門家を選ぶことも重要です。"
                "名前のみを返してください。"
            ),
            send_introductions=True,
        )

        return GroupChatManager(
            groupchat=group_chat,
            llm_config=select_speaker_llm_config,
        )

    def start_therapist_discussion(self, user_message, max_turns=10):
        """
        ユーザーの悩みに基づいてセラピスト間の議論を開始する
        """
        manager = self.create_group_chat(max_rounds=max_turns)

        initial_message = f"""
患者から次のような悩みが寄せられました：「{user_message}」

この悩みについて、それぞれの専門的観点から議論し、最適な支援方法を考えましょう。
各セラピストは以下のガイドラインに従って会話を進めてください：

1. 自分の専門分野からの視点を明確に共有する
2. 他のセラピストの意見に対して必ず質問や補足、同意/反対の意見を述べる
3. 他のセラピストの名前を明示的に呼びかけて対話する（例: 「〇〇さん、あなたの意見について...」）
4. 互いの専門知識を尊重しながらも、建設的な議論を行う
5. 患者の立場からも意見を述べる
6. 最終的に統合された支援プランを作成する

セラピスト同士の活発な対話を通じて、患者にとって最適な支援方法を見つけましょう。
単に順番に意見を述べるのではなく、互いの発言に対して反応し、議論を深めてください。
対話の中で質問を投げかけ、他のセラピストの視点を引き出すことも重要です。

最初のセラピストは、患者の悩みに対する初期評価と、他のセラピストへの質問から始めてください。
"""

        # 会話を開始（患者から始める）
        manager.initiate_chat(
            patient,
            message=initial_message,
        )

        # 会話履歴を文字列として整形
        conversation_history = self._format_conversation(manager.groupchat.messages)

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            # 表示名に変換（マッピングにない場合はそのまま使用）
            display_name = self.display_names.get(sender, sender)
            content = msg.get("content", "")
            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text


# シングルトンインスタンスを作成
counseling_group = CounselingGroupChat()
